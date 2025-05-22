#!/bin/bash
# Finds hidden virtual hosts  
IP=$1
DOMAIN=$2
OUT_DIR="gobuster/$IP/06_vhosts"

mkdir -p $OUT_DIR
gobuster vhost -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
  --append-domain \
  -t 20 \
  -o "$OUT_DIR/results.txt"