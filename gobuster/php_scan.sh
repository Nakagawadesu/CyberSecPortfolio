#!/bin/bash
# PHP-focused scan with version fingerprinting  
#!/bin/bash
source gobuster_wrapper.sh

echo "[*] Hunting PHP files on $DOMAIN..."
gobuster dir -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/Web-Content/PHP.fuzz.txt \
  -x php,phtml,phar \
  -t 25 \
  -o "$OUT_DIR/02_php_scan.txt"