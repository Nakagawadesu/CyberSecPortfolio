#!/bin/bash
# Discovers JSON API endpoints  
IP=$1
DOMAIN=$2
OUT_DIR="gobuster/$IP/04_api_endpoints"

mkdir -p $OUT_DIR
gobuster dir -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/Web/Common-Api-Endpoints.txt \
  -x json \
  -k \
  --wildcard \
  -t 15 \
  -o "$OUT_DIR/results.txt"