# Forensic Triage Scripts

A collection of Python scripts designed to automate and accelerate the initial analysis of Windows forensic triage images on a Linux-based analysis machine. These tools help in quickly understanding the evidence layout and processing key artifacts.
There will be added more script according to common situations that arise during foresic challanges

---

## 1. Directory & File Lister (`list_directories.py`)

This script generates a clean, tree-like view of all directories and the files within a specified path. It's incredibly useful for getting a quick, high-level overview of the collected evidence and finding the location of specific artifacts without manually navigating through complex folder structures.

### Usage

Run the script from your terminal, providing the path to your triage image as a command-line argument.

```bash
python3 list_directories.py /path/to/your/triage_image
```
Example Output
The script will print a structured list to your console, like this:
```bash

Directory and file tree for: /path/to/your/triage_image/

└── TRIAGE_IMAGE/
    ├── C/
    │   ├── Users/
    │   │   └── Cogwork_Admin/
    │   │       ├── NTUSER.DAT
    │   │       └── AppData/
    │   └── Windows/
    │       └── System32/
    │           ├── config/
    │           │   ├── SAM
    │           │   └── SYSTEM
    │           └── winevt/
    │               └── Logs/
    │                   └── Security.evtx
```

## 2. Automatic Artifact Processor (auto_triage.py)
This script automates the initial processing of key Windows forensic artifacts. It scans a triage image, identifies high-value files (like Event Logs, Registry Hives, and the $MFT), and automatically runs the appropriate Zimmerman's EZ Tool to parse them into a human-readable CSV format.

Prerequisites
- Before running this script, ensure you have the following installed and configured:

- Python 3

- Zimmerman's EZ Tools: Downloaded and extracted to a known location (e.g., /home/nukitaro/EZTools).

- .NET Runtime: Required to execute the EZ Tools' .dll files.

### Configuration
You must edit the configuration variables at the top of the auto_triage.py script to match the paths on your system.

```Python

# --- CONFIGURATION ---
# Base directory where your challenge files are.
DOWNLOADS_DIR = "/home/nukitaro/Downloads"

# Path to your Zimmerman EZTools folder (e.g., the .NET 9 version).
EZTOOLS_DIR = "/home/nukitaro/EZTools/net9"

# Full path to the dotnet executable.
DOTNET_PATH = "/home/nukitaro/.dotnet/dotnet"

# Name of the main output folder for all analysis.
ANALYSIS_FOLDER_NAME = "Analisys"
# --- END CONFIGURATION ---
```

Usage
Run the script from your terminal, providing the path to the root of the triage image you want to process.

```Bash

python3 auto_triage.py /path/to/your/triage_image
```

### How It Works
The script first creates an Analisys directory in your specified DOWNLOADS_DIR.

It recursively scans the entire triage image for known artifact filenames (e.g., Security.evtx, SYSTEM, $MFT).

For each artifact it finds, it automatically runs the correct Zimmerman tool (EvtxECmd, RECmd, MFTECmd, etc.).

It saves the processed output (as CSVs) into neatly organized subfolders within the Analisys directory, named after the artifact that was processed (e.g., Analisys/Security.evtx_parsed/).

This process automates the tedious first steps of an investigation, allowing the analyst to focus on the data immediately.