#!/bin/bash
set -euo pipefail

DATA_DIR="data"
BACKUP_DIR="backup"
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/download.log"

JUL_URL="https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log"
AUG_URL="https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log"

mkdir -p "$DATA_DIR" "$BACKUP_DIR" "$LOG_DIR"

timestamp() {
  date "+%Y-%m-%d %H:%M:%S"
}

log_msg() {
  echo "[$(timestamp)] $1" | tee -a "$LOG_FILE"
}

download_file() {
  local url="$1"
  local outfile="$2"

  log_msg "Starting download: $outfile"

  if ! curl -L --fail --retry 3 -o "$outfile" "$url"; then
    log_msg "ERROR: Failed to download $outfile"
    return 1
  fi

  if [[ ! -s "$outfile" ]]; then
    log_msg "ERROR: Downloaded file is empty: $outfile"
    return 1
  fi

  local line_count
  local file_size
  line_count=$(wc -l < "$outfile")
  file_size=$(wc -c < "$outfile")

  log_msg "Validated $outfile | lines=$line_count bytes=$file_size"

  cp "$outfile" "$BACKUP_DIR/$(basename "$outfile").bak"
  log_msg "Created backup: $BACKUP_DIR/$(basename "$outfile").bak"
}

log_msg "Download job started"
download_file "$JUL_URL" "$DATA_DIR/NASA_Jul95.log"
download_file "$AUG_URL" "$DATA_DIR/NASA_Aug95.log"
log_msg "Download job completed successfully"