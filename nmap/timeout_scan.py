#!/usr/bin/env python3
"""
Timeout-Protected Nmap Scanner
Features:
- 5-minute timeout per port scan
- Graceful error handling for hung scans
- Resource cleanup for interrupted scans
"""

import subprocess
import os
import re
import argparse
import signal
from datetime import datetime

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("Scan timed out")

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
    """Run scan with timeout protection"""
    cmd = f"nmap -T4 -sV -p {port} {target} -oN {output_dir}/port_{port}.txt"
    try:
        # Set 5-minute timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(300)
        
        process = subprocess.Popen(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        with open(f"{output_dir}/port_{port}.txt", "w") as f:
            f.write(stdout.decode())
            
    except TimeoutException:
        print(f"[-] Port {port} scan aborted (timeout)")
        if process:
            process.kill()
    finally:
        signal.alarm(0)
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