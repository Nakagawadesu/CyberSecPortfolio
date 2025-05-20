#!/bin/bash
# PHP-focused scan with version fingerprinting  
IP=$1
DOMAIN=$2
OUT_DIR="gobuster/$IP/02_files_php"

mkdir -p $OUT_DIR
gobuster dir -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/Web-Content/PHP.fuzz.txt \
  -x php,phtml,phar \
  --exclude-length 0 \
  -t 30 \
  -o "$OUT_DIR/results.txt"