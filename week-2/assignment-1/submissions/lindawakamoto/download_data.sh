#!/bin/bash
set -euo pipefail

LOGFILE="pipeline.log"
DATA_DIR="data"
BACKUP_DIR="backup"

mkdir -p "$DATA_DIR" "$BACKUP_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"
}

download_file() {
  local url="$1"
  local file="$2"
  local path="$DATA_DIR/$file"

  log "Starting download: $file"

  if curl -L --fail --show-error \
    --retry 5 --retry-delay 2 --retry-connrefused \
    --connect-timeout 10 \
    --max-time 600 \
    "$url" -o "$path"; then
    log "Downloaded: $file"
  else
    log "ERROR: download failed: $file"
    return 1
  fi

  if [[ ! -s "$path" ]]; then
    log "ERROR: empty file: $file"
    return 1
  fi

  local size lines
  size=$(wc -c < "$path")
  lines=$(wc -l < "$path")

  if (( size < 1000000 || lines < 1000 )); then
    log "ERROR: validation failed (too small): $file"
    return 1
  fi

  log "Validated: $file (${size} bytes, ${lines} lines)"

  cp -f "$path" "$BACKUP_DIR/$file.bak"
  log "Backup created: $file.bak"
}

log "Pipeline started"

if download_file "https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log" "NASA_Jul95.log" && \
   download_file "https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log" "NASA_Aug95.log"; then
  log "SUCCESS: All downloads completed"
else
  log "FAILURE: Download stage failed"
  exit 1
fi

log "Done"