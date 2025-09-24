#!/bin/bash
# Targets IIS servers with ASP/XSS extensions
#!/bin/bash
source gobuster_wrapper.sh

echo "[*] Targeting IIS at $DOMAIN..."
gobuster dir -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/Web-Content/IIS.fuzz.txt \
  -x aspx,ashx,asmx,config \
  --user-agent "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)" \
  -o "$OUT_DIR/03_iis_scan.txt"