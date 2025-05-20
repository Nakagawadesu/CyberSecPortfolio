#!/bin/bash
# Stealthy directory scan with random delays/user-agent
IP=$1
DOMAIN=$2
OUT_DIR="gobuster/$IP/01_dir_stealth"

mkdir -p $OUT_DIR
gobuster dir -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt \
  -x html,php,txt \
  -t 20 \
  --delay 300-700ms \
  --random-agent \
  --no-error \
  -o "$OUT_DIR/results.txt"