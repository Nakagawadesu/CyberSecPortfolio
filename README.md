# Cybersecurity Portfolio & Automation Lab

Welcome to my cybersecurity portfolio! This repository serves as a collection of my work, methodologies, and custom tools developed during my journey through various cybersecurity challenges. I have a passion for digital forensics and offensive security, and I especially enjoy practicing my skills on platforms like Hack The Box.
I like to document it so i can use it for consulting because I sometimes forget small details that possibly a chlalnge i made in the past might help me with

This space is divided into three main areas: detailed CTF write-ups, reconnaissance scripts, and forensic automation tools.

---

## 📂 Directory Structure

Here's an overview of how the repository is organized:
```bash
/
├── Write_ups/
│   └── [Platform_ChallengeName_Date]/  #CTFS that i participate...
│   └── [Category(Sherlokc, POWN]/ #has teh name of the category of challange sehrlokcs are blue team and so on...
│                           
└── Ressoinance_Automations/
│   └── Forensic_Automations/  #Forensic and investigaition related automations
│   ├── Ressoinance_Automations/ #Pentest Related automations
```
---

## 📝 Write-ups

This directory contains detailed, step-by-step walkthroughs of Capture The Flag (CTF) challenges I have solved. Each write-up documents the complete investigation, from initial analysis to final flag capture, explaining the tools, techniques, and forensic artifacts involved.

My goal is to not only solve challenges but to understand the "why" behind each step, creating a valuable knowledge base for myself and others in the community.

### Featured Write-ups
* **The Enduring Echo**: A Windows host analysis involving SSH, WMI, persistence mechanisms, and network pivoting.
* **Holmes HTB**: [Briefly describe another challenge here]

---

## 🕵️ Ressoinance (Reconnaissance) Automations

This section contains custom scripts I've written to automate and streamline the reconnaissance phase of security assessments. The goal is to perform scans more efficiently, quietly, or in greater detail, depending on the engagement's requirements.

* **Nmap Scripts**: A collection of Python wrappers for `nmap` that automate various scanning techniques, such as stealth scans, top-port scans, and faster, multi-threaded scans.
* **Gobuster Scripts**: A set of shell scripts for `gobuster` tailored to specific web application targets, including APIs, PHP sites, and IIS servers.

---

## 🔬 Forensic Automations

Here you will find Python scripts created to speed up the initial triage and analysis of forensic artifacts. Dealing with binary files and large logs during a time-sensitive challenge can be difficult, so these tools automate the repetitive tasks of listing evidence, parsing binary formats, and filtering data.

* **`list_directories.py`**: A simple utility to generate a clean, tree-like view of a forensic image's directory structure.
* **`auto_triage_ZTools.sh`**: A powerful script that scans a Windows triage image, identifies key artifacts (Event Logs, Registry Hives, $MFT), and automatically runs the appropriate Zimmerman's EZ Tool to process them into human-readable CSVs.
* **`log_filter.py`**:
This script is designed to quickly filter and search large CSV log files. It's particularly useful for event logs parsed by tools like Eric Zimmerman's EvtxECmd, allowing you to narrow down thousands of entries by specific keywords and timestamps. This updated version now saves the filtered results to a new CSV file, making it easier to share or analyze the relevant data separately. The output filename is automatically generated to include the original filename and the keywords used for filtering.


---

Feel free to explore the repository, and I hope you find the content both interesting and useful!
