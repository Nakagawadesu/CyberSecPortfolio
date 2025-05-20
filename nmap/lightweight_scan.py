#!/usr/bin/env python3
"""
Lightweight Nmap Scanner with Essential Scripts Only
Features:
- Runs only banner grabbing script (--script=banner)
- Avoids resource-intensive NSE scripts
- Maintains fast timing profile
"""

import subprocess
import os
import re
import argparse
from datetime import datetime

def create_output_dir(target: str) -> str:
    """Create organized output directory with timestamp
    Args:
        target: IP/hostname being scanned
    Returns:
        Path to created directory (format: nmap/<target>_<timestamp>)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"nmap/{target}_{timestamp}"
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

def run_initial_scan(target: str) -> list:
    """Perform initial fast port discovery
    Uses:
        -sS: SYN Stealth Scan (fast, doesn't complete TCP handshake)
        -T4: Aggressive timing template (6 parallel probes, shorter delays)
    """
    print(f"[*] Starting initial SYN scan on {target}")
    cmd = f"nmap -T4 -sS --min-rate 1000 {target}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    # Extract open ports using regex
    return re.findall(r"(\d+)/tcp\s+open", result.stdout)


def run_detailed_scan(target: str, port: str, output_dir: str) -> None:
    """Lightweight service detection with critical scripts only
    Parameters:
        --script=banner: Run only banner grab script
        --version-intensity 1: Quick version check
        -Pn: Treat all hosts as online (skip host discovery)
    """
    cmd = (
        f"nmap -T4 -Pn --script=banner --version-intensity 1 "
        f"-sV -p {port} {target} -oN {output_dir}/port_{port}.txt"
    )
    subprocess.run(cmd.split())


def main():
    parser = argparse.ArgumentParser(description="Optimized Timing Nmap Scanner")
    parser.add_argument("target", help="IP/hostname to scan")
    args = parser.parse_args()
    
    output_dir = create_output_dir(args.target)
    open_ports = run_initial_scan(args.target)
    
    if open_ports:
        print(f"[*] Found {len(open_ports)} open ports. Starting detailed scans...")
        for port in open_ports:
            run_detailed_scan(args.target, port, output_dir)
        print("[+] Scan sequence completed")
    else:
        print("[-] No open ports found")

if __name__ == "__main__":
    main()