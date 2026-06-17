#!/bin/bash

DATA_DIR="data"
BACKUP_DIR="backup"
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/download.log"

mkdir -p "$DATA_DIR" "$BACKUP_DIR" "$LOG_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

download_with_retries() {
  local url=$1
  local output=$2
  local max_retries=3
  local retry=0

  while [ $retry -lt $max_retries ]; do
    log "Attempting download from $url (attempt $((retry + 1))/$max_retries)"
    if curl -f -s "$url" > "$output"; then
      return 0
    else
      retry=$((retry + 1))
      if [ $retry -lt $max_retries ]; then
        log "Download failed, retrying in 2 seconds..."
        sleep 2
      fi
    fi
  done

  log "Failed to download after $max_retries attempts: $url"
  return 1
}

log "Starting NASA web server log download"

# Process July log
log "Processing NASA_Jul95.log..."
if download_with_retries "https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log" "$DATA_DIR/NASA_Jul95.log"; then
  log "Downloaded NASA_Jul95.log successfully"

  # Validate July log
  JULY_SIZE=$(wc -c < "$DATA_DIR/NASA_Jul95.log")
  JULY_LINES=$(wc -l < "$DATA_DIR/NASA_Jul95.log")

  if [[ "$JULY_SIZE" -gt 0 && "$JULY_LINES" -gt 0 ]]; then
    log "Validated NASA_Jul95.log: $JULY_SIZE bytes, $JULY_LINES lines"
    # Backup July log
    cp "$DATA_DIR/NASA_Jul95.log" "$BACKUP_DIR/NASA_Jul95.log.bak"
    log "Created backup for NASA_Jul95.log"
  else
    log "ERROR: NASA_Jul95.log validation failed - skipping backup"
  fi
else
  log "ERROR: Failed to download NASA_Jul95.log - skipping validation and backup"
fi

# Process August log
log "Processing NASA_Aug95.log..."
if download_with_retries "https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log" "$DATA_DIR/NASA_Aug95.log"; then
  log "Downloaded NASA_Aug95.log successfully"

  # Validate August log
  AUG_SIZE=$(wc -c < "$DATA_DIR/NASA_Aug95.log")
  AUG_LINES=$(wc -l < "$DATA_DIR/NASA_Aug95.log")

  if [[ "$AUG_SIZE" -gt 0 && "$AUG_LINES" -gt 0 ]]; then
    log "Validated NASA_Aug95.log: $AUG_SIZE bytes, $AUG_LINES lines"
    # Backup August log
    cp "$DATA_DIR/NASA_Aug95.log" "$BACKUP_DIR/NASA_Aug95.log.bak"
    log "Created backup for NASA_Aug95.log"
  else
    log "ERROR: NASA_Aug95.log validation failed - skipping backup"
  fi
else
  log "ERROR: Failed to download NASA_Aug95.log - skipping validation and backup"
fi

log "Download process completed"