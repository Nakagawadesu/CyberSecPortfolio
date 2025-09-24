#!/bin/bash
TARGET="$1"
OUT_BASE="results"

# 1. Parameter Validation
if [ -z "$TARGET" ]; then
  echo "Usage: $0 <IP_OR_DOMAIN>"
  exit 1
fi

# 2. IP/Domain Auto-Detection
if [[ "$TARGET" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
  IP="$TARGET"
  DOMAIN="$IP"  # Treat IP as domain for URL construction
else
  DOMAIN="$TARGET"
  # 3. DNS Resolution (Supports /etc/hosts entries)
  IP=$(getent hosts "$DOMAIN" | awk '{print $1}' | head -n1)
  [ -z "$IP" ] && echo "Error: Can't resolve $DOMAIN" && exit 1
fi

# 4. Sanitized Output Directory
SANITIZED_IP=$(echo "$IP" | tr '.' '_')  # 10.129.95.234 → 10_129_95_234
OUT_DIR="$OUT_BASE/$SANITIZED_IP"
mkdir -p "$OUT_DIR"