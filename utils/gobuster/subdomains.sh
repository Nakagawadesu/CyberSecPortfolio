#!/bin/bash
source gobuster_wrapper.sh

echo "[*] Brute-forcing subdomains for $DOMAIN..."
gobuster dns -d "$DOMAIN" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
  --resolver 1.1.1.1 \
  -o "$OUT_DIR/05_subdomains.txt"