#  DFIR Challenge Write-up: PowerShell Reconnaissance
## Overview
This report details the forensic analysis performed on two Windows Event Log files: Microsoft-Windows-Powershell.evtx (Console Log) and Windows-Powershell-Operational.evtx (Script/Detailed Log). The goal was to reconstruct the attacker's system reconnaissance activities, specifically focusing on attempts to detect virtualization environments and gather system metrics.

- Tools and Methodology
The primary challenge involved correlating data across two large event log files.

- Initial Triage: Eric Zimmerman's EvtxECmd.dll was used to parse both .evtx files and output the contents into structured CSV formats for easier filtering and analysis.

- Targeted Filtering: Due to the size of the logs, a custom Python script, log_filter_strict.py, was used. This script allowed for fast, precise filtering using multiple keywords (e.g., combining a timestamp with a specific command/function keyword) to isolate individual suspicious log entries (Event IDs 4104 and 800) from the noisy operational logs.

# Example command using the custom Python script

```python 
python log_filter_strict.py powershell_operational.csv "2025-04-09 09:20:53" "function"
```

## Task Solutions (Flags)
### Task 1: WMI Class for Virtualization Detection
The attacker's initial steps involved using Windows Management Instrumentation (WMI) to gather basic system information.

Question: Which WMI class did the attacker use to retrieve model and manufacturer information for virtualization detection?

Analysis: Searching the Microsoft-Windows-Powershell.evtx logs for "Wmi" quickly led to a command using the -Class parameter to query system hardware details.
```bash
... CommandLine=$Manufacturer = Get-WmiObject -Class Win32_ComputerSystem | select-object -expandproperty "Manufacturer" ...
```
<img width="1583" height="165" alt="PahtomCheck FirstDFlag " src="https://github.com/user-attachments/assets/681c4dc2-8944-45e0-9530-3e4c0c395aee" />

```bash
Answer: Win32_ComputerSystem
```
### Task 2: WMI Temperature Query
The attacker continued system profiling by attempting to query sensor data, another common technique to distinguish between virtualized and physical hosts.

Question: Which WMI query did the attacker execute to retrieve the current temperature value of the machine?
<img width="1620" height="100" alt="Phatom Check SecodGFlag" src="https://github.com/user-attachments/assets/57a40c49-5a87-4c00-b0d0-0514b8fa5b27" />

Analysis: A subsequent log entry revealed another Get-WmiObject command, this time using the -Query parameter to target the thermal zone class.
```bash 
Answer: SELECT * FROM MSAcpi_ThermalZoneTemperature
```
### Task 3: Virtualization Detection Script Function
The attacker then executed a full script block to perform a comprehensive virtualization check.
<img width="1306" height="364" alt="PahtomCheckVirtualizationFlag" src="https://github.com/user-attachments/assets/44a845e1-de08-42a3-bcc9-7bdbc20310b9" />

Question: The attacker loaded a PowerShell script to detect virtualization. What is the function name of the script?
<img width="1582" height="207" alt="PahtomCheck_CehckVM3Flag" src="https://github.com/user-attachments/assets/3951a1ff-b983-44d4-b25c-317a3725d27c" />

Analysis: By combining the timestamps of the malicious activity with the keyword "function" using log_filter_strict.py on the Operational Log (Event ID 4104), the entire script block was retrieved. The script is identified as being part of the Nishang framework. The function definition was clearly visible at the top of the block.
```bash 
function Check-VM, {, <# , .SYNOPSIS , Nishang script which detects whether it is in a known virtual machine. ... #>
```
```bash
Answer: Check-VM
```
### Task 4: Registry Key for Service Detection
The identified script, Check-VM, performs numerous checks on the system, including querying the Windows Registry for common virtual machine service artifacts.

Question: Which registry key did the above script query to retrieve service details for virtualization detection?

Analysis: Detailed examination of the Check-VM script's content (Task 3 log entry) revealed multiple instances where the Get-ChildItem cmdlet was used to query subkeys under a specific path for Hyper-V, VMWare, and Virtual PC service names (e.g., vmicheartbeat, vmmouse, vpc-s3).
```bash 
... $hyperv = Get-ChildItem HKLM:\SYSTEM\ControlSet001\Services ...
```
<img width="1280" height="174" alt="PahntomCheckFlag4" src="https://github.com/user-attachments/assets/ae88c177-5c5c-4e27-b672-842c11a49282" />

Answer: HKLM:\SYSTEM\ControlSet001\Services

### Task 5: VirtualBox Detection Processes
The Check-VM script checks for multiple virtualization platforms, including VirtualBox, by checking for running processes and installed services.

Question: The VM detection script can also identify VirtualBox. Which processes is it comparing to determine if the system is running VirtualBox?

Analysis: Analyzing the section of the Check-VM script dedicated to VirtualBox detection reveals the explicit process names being checked using Get-Process.

#Virtual Box
```bash 
$vb = Get-Process,
if (($vb -eq "vboxservice.exe") -or ($vb -match "vboxtray.exe"))
```
### Task 6: Detected Virtualization Platforms
Finally, analyzing the output messages generated by the executed script reveals which environments the attacker successfully detected.

Question: The VM detection script prints any detection with the prefix 'This is a'. Which two virtualization platforms did the script detect?

Analysis: The output logs contain the conditional print statements from the Check-VM script that confirm virtualization detection. The key phrases found are:
<img width="1028" height="118" alt="PahtohomCHek LAstFlag1" src="https://github.com/user-attachments/assets/7d22a1fa-220e-4112-b63f-26ba17837da3" />

"This is a Hyper-V machine."

"This is a VMWare machine."
``` bash 
Answer: Hyper-V, Vmware
```
