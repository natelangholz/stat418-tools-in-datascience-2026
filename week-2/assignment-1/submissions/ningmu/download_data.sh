#!/bin/bash
# download_data.sh - Download, validate, and backup NASA web server logs
# Usage: ./download_data.sh

set -euo pipefail

LOGFILE="download.log"
DATA_DIR="data"
BACKUP_DIR="backup"

# create Directory
mkdir -p "$DATA_DIR" "$BACKUP_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"
}

download() {
  local url=$1
  local filename=$2

  log "Downloading $filename..."

  if curl -f -sS "$url" -o "$DATA_DIR/$filename"; then
    log "Download successful: $filename"
  else
    log "Download failed: $filename"
    exit 1
  fi

  # verify the file
  if [[ ! -s "$DATA_DIR/$filename" ]]; then
    log "Error: $filename is empty"
    exit 1
  fi

  lines=$(wc -l < "$DATA_DIR/$filename")
  size=$(wc -c < "$DATA_DIR/$filename")

  log "Validated $filename | Lines: $lines | Size: $size bytes"

  # backup
  cp "$DATA_DIR/$filename" "$BACKUP_DIR/$filename.bak"
  log "Backup created: $filename.bak"
}

log "Starting download process..."

download "https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log" "NASA_Jul95.log"
download "https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log" "NASA_Aug95.log"

log "All downloads completed!"