#!/bin/bash
# Subdomain scan with DNS resolver rotation  
IP=$1
DOMAIN=$2
OUT_DIR="gobuster/$IP/05_subdomains"

mkdir -p $OUT_DIR
gobuster dns -d "$DOMAIN" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
  --resolver 1.1.1.1,8.8.8.8,9.9.9.9 \
  --show-ips \
  -t 40 \
  -o "$OUT_DIR/results.txt"