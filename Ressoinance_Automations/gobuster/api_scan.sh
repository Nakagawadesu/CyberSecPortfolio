#!/bin/bash
# Discovers JSON API endpoints  
#!/bin/bash
source gobuster_wrapper.sh

echo "[*] Finding API endpoints on $DOMAIN..."
gobuster dir -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/Web/Common-Api-Endpoints.txt \
  -x json \
  -k \
  -o "$OUT_DIR/04_api_scan.txt"