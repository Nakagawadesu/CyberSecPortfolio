#!/usr/bin/env python3
"""
Fully Optimized Nmap Automation Script
Combines:
- Aggressive timing (-T4)
- Lightweight version detection (--version-intensity 2)
- Essential scripting (--script=banner)
- Parallel execution (threading)
- Timeout protection (300s)
- Organized output structure
"""

import subprocess
import os
import re
import argparse
import threading
from datetime import datetime

MAX_THREADS = 5
TIMEOUT = 300  # 5 minutes

def create_output_dir(target: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"results/{target}_{timestamp}"
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

def run_initial_scan(target: str) -> list:
    print(f"[*] Starting initial scan on {target}")
    cmd = f"nmap -T4 -sS --min-rate 1000 {target}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    return re.findall(r"(\d+)/tcp\s+open", result.stdout)

def run_detailed_scan(target: str, port: str, output_dir: str) -> None:
    """Optimized scan with all improvements"""
    try:
        cmd = (
            f"nmap -T4 -Pn --script=banner --version-intensity 2 "
            f"-sV -p {port} {target} -oN {output_dir}/port_{port}.txt"
        )
        process = subprocess.Popen(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(timeout=TIMEOUT)
        
        with open(f"{output_dir}/port_{port}.txt", "w") as f:
            f.write(stdout.decode())
            
    except subprocess.TimeoutExpired:
        print(f"[-] Port {port} scan timed out")
        process.kill()

def main():
    parser = argparse.ArgumentParser(description="Optimized Nmap Automation")
    parser.add_argument("target", help="Target IP/hostname")
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
        
        print("[+] All optimized scans completed")

if __name__ == "__main__":
    main()