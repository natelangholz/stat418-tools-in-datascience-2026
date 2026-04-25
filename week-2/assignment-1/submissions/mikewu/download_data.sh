#!/bin/bash
# download_data.sh - Download NASA logs, validate, keep backups and a log file.

set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${1:-$HERE/data}"

mkdir -p "$DATA_DIR"
mkdir -p "$DATA_DIR/logs"

LOG="$DATA_DIR/logs/download.log"

JUL_URL="https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log"
AUG_URL="https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log"
JUL="$DATA_DIR/NASA_Jul95.log"
AUG="$DATA_DIR/NASA_Aug95.log"

stamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

echo "[$(stamp)] DATA_DIR=$DATA_DIR" >>"$LOG"
echo "[$(stamp)] DATA_DIR=$DATA_DIR"

BACKUP="$DATA_DIR/backups/backup_$(date -u +%Y%m%d_%H%M%S)"

if [ -f "$JUL" ]; then
  mkdir -p "$BACKUP"
  cp -p "$JUL" "$BACKUP/"
  echo "[$(stamp)] Backed up NASA_Jul95.log to $BACKUP" | tee -a "$LOG"
fi

if [ -f "$AUG" ]; then
  mkdir -p "$BACKUP"
  cp -p "$AUG" "$BACKUP/"
  echo "[$(stamp)] Backed up NASA_Aug95.log to $BACKUP" | tee -a "$LOG"
fi

echo "Downloading NASA web server logs..."

echo "[$(stamp)] GET $JUL_URL" >>"$LOG"
curl -fsSL "$JUL_URL" -o "$JUL.tmp" || {
  echo "[$(stamp)] ERROR: could not download July log" | tee -a "$LOG"
  rm -f "$JUL.tmp"
  exit 1
}
mv "$JUL.tmp" "$JUL"
echo "Downloaded NASA_Jul95.log"
echo "[$(stamp)] OK NASA_Jul95.log" >>"$LOG"

echo "[$(stamp)] GET $AUG_URL" >>"$LOG"
curl -fsSL "$AUG_URL" -o "$AUG.tmp" || {
  echo "[$(stamp)] ERROR: could not download August log" | tee -a "$LOG"
  rm -f "$AUG.tmp"
  exit 1
}
mv "$AUG.tmp" "$AUG"
echo "Downloaded NASA_Aug95.log"
echo "[$(stamp)] OK NASA_Aug95.log" >>"$LOG"

for name in "NASA_Jul95.log" "NASA_Aug95.log"; do
  f="$DATA_DIR/$name"
  bytes=$(wc -c <"$f" | tr -d ' ')
  lines=$(wc -l <"$f" | tr -d ' ')
  echo "[$(stamp)] $name size=$bytes bytes lines=$lines" | tee -a "$LOG"
  if [ "$bytes" -lt 5000000 ]; then
    echo "[$(stamp)] ERROR: $name looks too small ($bytes bytes)" | tee -a "$LOG"
    exit 1
  fi
  if [ "$lines" -lt 100000 ]; then
    echo "[$(stamp)] ERROR: $name has too few lines ($lines)" | tee -a "$LOG"
    exit 1
  fi
done

echo "Download complete!"
echo "[$(stamp)] All checks passed." >>"$LOG"
