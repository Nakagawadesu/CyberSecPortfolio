#!/usr/bin/env python3
import subprocess
import os
import re
import argparse
from datetime import datetime

def create_output_dir(target):
    """Create output directory in /nmap/<target>_<timestamp>"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name = f"results/{target}_{timestamp}"
    os.makedirs(dir_name, exist_ok=True)
    return dir_name

def run_initial_scan(target):
    """Run initial quick scan to find open ports"""
    print(f"[*] Starting initial scan on {target}")
    cmd = f"nmap -v -sS {target}"
    result = subprocess.run(cmd.split(), capture_output=True, text=True)
    
    open_ports = []
    for line in result.stdout.split('\n'):
        if "Discovered open port" in line:
            port = re.search(r'(\d+)/tcp', line).group(1)
            open_ports.append(port)
            print(f"[+] Found open port: {port}/tcp")
    
    return open_ports

def run_detailed_scan(target, port, output_dir):
    """Run detailed version scan on specific port"""
    print(f"[*] Scanning port {port} with -sV")
    cmd = f"nmap -v -sV -p {port} {target} -oN {output_dir}/port_{port}_scan.txt"
    subprocess.run(cmd.split())

def main():
    parser = argparse.ArgumentParser(description="Automated Nmap Scanner")
    parser.add_argument("target", help="IP address or domain to scan")
    args = parser.parse_args()

    output_dir = create_output_dir(args.target)
    open_ports = run_initial_scan(args.target)

    if open_ports:
        print(f"[*] Starting detailed scans in {output_dir}")
        for port in open_ports:
            run_detailed_scan(args.target, port, output_dir)
        print("[+] All scans completed!")
    else:
        print("[-] No open ports found")

if __name__ == "__main__":
    main()