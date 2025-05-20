#!/usr/bin/env python3
"""
Multithreaded Nmap Scanner
Features:
- Parallel port scanning using threading
- Configurable thread pool size
- Thread-safe output writing
"""

import subprocess
import os
import re
import argparse
import threading
from datetime import datetime

MAX_THREADS = 5  # Conservative thread count for stability

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
    """Thread-safe detailed scan execution"""
    cmd = f"nmap -T4 -sV -p {port} {target} -oN {output_dir}/port_{port}.txt"
    try:
        result = subprocess.run(
            cmd.split(),
            capture_output=True,
            text=True,
            timeout=300
        )
        with open(f"{output_dir}/port_{port}.txt", "w") as f:
            f.write(result.stdout)
    except subprocess.TimeoutExpired:
        print(f"[-] Port {port} scan timed out")

def main():
    parser = argparse.ArgumentParser(description="Multithreaded Nmap Scanner")
    parser.add_argument("target", help="IP/hostname to scan")
    args = parser.parse_args()
    
    output_dir = create_output_dir(args.target)
    open_ports = run_initial_scan(args.target)
    
    if open_ports:
        print(f"[*] Starting {len(open_ports)} scans with {MAX_THREADS} threads")
        semaphore = threading.Semaphore(MAX_THREADS)
        threads = []
        
        for port in open_ports:
            semaphore.acquire()
            thread = threading.Thread(
                target=run_detailed_scan,
                args=(args.target, port, output_dir)
            )
            thread.start()
            threads.append(thread)
            semaphore.release()
        
        for thread in threads:
            thread.join()
        
        print("[+] Parallel scanning completed")

if __name__ == "__main__":
    main()