# Digital Forensics Report: The Enduring Echo Incident

**Analyst:** nukitaro
**Date:** 2025-09-23

---

## 1.0 Executive Summary

This report details the forensic analysis of a compromised Windows host, codenamed "Heisen-9-WS-6". The investigation revealed a multi-stage attack that began with initial access via SSH. The threat actor then established multiple layers of persistence, including creating two new user accounts (`Werni` and `svc_netupd`) and a malicious scheduled task (`SysHelper Update`). The attacker performed reconnaissance using built-in Windows tools, executed commands remotely via WMI, and modified the system's `hosts` file to ensure resilient command-and-control (C2) communication. The final stage of the attack involved setting up a TCP port forward to pivot from the compromised host to another target on the internal network.

---

## 2.0 Tools Used

* **KAPE (Kroll Artifact Parser and Extractor)**: Used for the initial collection of forensic artifacts from the host.
* **Zimmerman's EZ Tools**: A suite of forensic tools used for analysis.
    * **`EvtxECmd.dll`**: A powerful command-line event log (`.evtx`) parser used to convert binary event logs into human-readable CSV format.
    * **`RECmd.dll`**: A command-line registry hive parser used to search for and extract specific keys and values from offline registry files.
* **Visual Studio Code**: A versatile text editor used to view and search the contents of large CSV log files, scripts, and other text-based artifacts. The built-in search (`Ctrl + F`) was essential for quickly finding keywords.
* **Python 3**: Used with the `csv` and `re` modules to write custom scripts for filtering and creating condensed timelines from the large CSV log files.
* **Standard Linux Command-Line Tools**:
    * **`grep`**: Used to search for keywords and create smaller, filtered files from the main CSV outputs.

---

## 3.0 Investigation Timeline & Analysis

The analysis followed the evidence chronologically, beginning with the attacker's entry point and tracing their actions through various system artifacts.

### 3.1 Initial Log Processing and Filtering

The investigation began by parsing the main Security Event Log (`Security.evtx`) to convert it into a searchable format.

* **Tool**: `EvtxECmd.dll`
* **Command**: `sudo /home/nukitaro/.dotnet/dotnet /home/nukitaro/EZTools/net9/EvtxeCmd/EvtxECmd.dll -f "/home/nukitaro/Downloads/The_Enduring_Echo/C/Windows/System32/winevt/logs/Security.evtx" --csv /home/nukitaro/Downloads/The_Enduring_Echo/Analisys`

This command created a large CSV file containing thousands of events. To make the analysis manageable, we created a Python script to isolate only the events from the primary day of the attack, **`2025-08-24`**.

* **Tool**: Python 3 (`condense_timeline_by_date.py`)
* **Purpose**: This script reads the large event log CSV but only pulls out the Time, User, and Command for events that occurred on the specified date, making the dataset much smaller and easier to analyze.

*[Leave space here for a screenshot of your date-filtering Python script in VS Code]*

### 3.2 Initial Access & Reconnaissance

With the logs filtered to the correct day, we opened the new CSV in Visual Studio Code to search for the attacker's entry point.

* **Analysis**: By using the search function (`Ctrl + F`) in VS Code on the filtered CSV for **Event ID 4624 (Successful Logon)**, we identified a remote logon (Logon Type 3) for the `Administrator` account originating from the attacker's IP address. This IP was later confirmed as the flag. Further analysis of process creation events (Event ID 4688) revealed that most of the attacker's subsequent non-interactive commands were spawned by `WmiPrvSE.exe`, the signature of a WMI-based remote execution tool like `wmiexec.py`.

The first command executed by the attacker was found by reviewing the chronological list of process creation events on the day of the attack. After an initial `cd` command, the attacker ran `systeminfo` to gather information about the host.

*[Leave space here for a screenshot in VS Code of the 'systeminfo' command in your condensed timeline CSV]*

### 3.3 Persistence Mechanisms

The attacker immediately took steps to ensure they could maintain access to the machine.

#### Stage 1: New User Account (`Werni`)

Analysis of the `Administrator`'s PowerShell history (`C:\Users\Administrator\...\ConsoleHost_history.txt`) showed the first persistence action. The command `net user Werni Quantum1! /add` was used, establishing their initial foothold.

#### Stage 2: Malicious Scheduled Task (`SysHelper Update`)

The attacker used the `schtasks.exe` command (found via Event ID 4688) to create a scheduled task. We analyzed the task's configuration file.

* **Artifact**: `C:\Windows\System32\Tasks\SysHelper Update`
* **Analysis**: Opening this XML file in VS Code revealed it was configured to run a PowerShell script every two minutes as the all-powerful `SYSTEM` user, representing a privilege escalation.

*[Leave space here for a screenshot of the XML content of the 'SysHelper Update' task file in VS Code]*

#### Stage 3: The Payload Script (`JM.ps1`) and Second User (`svc_netupd`)

Analysis of the `JM.ps1` script revealed its true purpose: to create a second, stealthier user account and exfiltrate the credentials.

* **Script Logic**: The script randomly selects a name, generates a password based on the current timestamp (`"Watson_" + timestamp`), creates the user, and adds it to the Administrators group.
* **Finding the Password**: We reconstructed the password by finding the creation time of the `svc_netupd` user (**Event ID 4720**) and applying the script's logic, accounting for a 7-hour time zone difference between the UTC log time (`23:05:09`) and the machine's local time (`16:05:09`).

### 3.4 Pivoting and Lateral Movement

The final phase of the attack involved setting up the compromised machine to be used as a pivot point.

#### Stage 1: C2 and DNS Hijacking

The attacker modified the `hosts` file to point a C2 domain to their own IP address, ensuring a resilient connection. This was discovered in the process creation logs (Event ID 4688) via the command: `echo 10.129.242.110 NapoleonsBlackPearl.htb >> C:\Windows\System32\drivers\etc\hosts`.

#### Stage 2: Port Forwarding

The attacker used the `netsh` command to set up a port forwarding rule. This was also found in the process creation logs (Event ID 4688). This command stores its configuration in the Windows Registry. We used `RECmd` to parse the `SYSTEM` hive to find the exact location and confirm the port. Analysis of the `known_hosts` file confirmed that the attacker successfully connected from the victim machine to the pivot target.

*[Leave space here for a screenshot of the 'netsh' command in your timeline, and another for the Registry Explorer view of the PortProxy key]*

---

## 4.0 Summary of Findings (Flags)

| Question | Answer |
| :--- | :--- |
| **First (non-cd) command executed?** | `systeminfo` |
| **Parent process of attacker's commands?** | `C:\Windows\System32\wbem\WmiPrvSE.exe` |
| **Remote-execution tool most likely used?** | `wmiexec.py` |
| **Attacker’s IP address?** | `10.129.242.110` |
| **First element in persistence sequence?** | `T1136.001` |
| **Script executed by persistence?** | `C:\Users\Werni\Appdata\Local\JM.ps1` |
| **Local account created by attacker?** | `svc_netupd` |
| **Domain for credential exfiltration?** | `NapoleonsBlackPearl.htb` |
| **Password generated by attacker's script?** | `Watson_20250824160509` |
| **IP address of internal pivot target?** | `192.168.1.101` |
| **TCP port forwarded for pivot?** | `9999` |
| **Full registry path for port mappings?** | `HKLM\SYSTEM\CurrentControlSet\Services\PortProxy\v4tov4\tcp` |
| **MITRE ATT&CK ID for pivot technique?** | `T1090.001` |
| **Admin command for command-line logging?** | `reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f` |