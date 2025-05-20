#!/bin/bash
# Targets IIS servers with ASP/XSS extensions
IP=$1
DOMAIN=$2
OUT_DIR="gobuster/$IP/03_files_iis"

mkdir -p $OUT_DIR
gobuster dir -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/Web-Content/IIS.fuzz.txt \
  -x aspx,ashx,asmx,config \
  --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124" \
  -t 25 \
  -o "$OUT_DIR/results.txt"