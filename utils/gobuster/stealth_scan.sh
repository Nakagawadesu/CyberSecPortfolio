#!/bin/bash
# Stealthy directory scan with random delays/user-agent
#!/bin/bash
source gobuster_wrapper.sh

echo "[*] Running stealth scan on $DOMAIN..."
gobuster dir -u "http://$DOMAIN" \
  -w /usr/share/seclists/Discovery/Web-Content/raft-small-words.txt \
  -x html,php,txt \
  --delay 500ms \
  --random-agent \
  -o "$OUT_DIR/01_stealth_scan.txt"