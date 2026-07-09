#!/bin/bash

# -e halts script if any command fails
# -u halts script if variable is not defined
# -o pipefail halts script if any command fails
set -euo pipefail

JULY_URL="https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log"
AUG_URL="https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log"
JULY_FILE="NASA_Jul95.log"
AUG_FILE="NASA_Aug95.log"
BACKUP_DIR="backups"
LOG_FILE="download_log.txt"

# defines function to log date into the log file
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# downloads file; outputs logging error into log if download fails
download_file() {
    local url="$1"       # The URL to download from
    local filename="$2"  # What to save it as

    log "Downloading $filename ..."

    if curl -f -L --progress-bar "$url" -o "$filename"; then
        log "SUCCESS: $filename downloaded."
    else
        log "ERROR: Failed to download $filename."
        exit 1
    fi
}

#  ensure file exists and is nonempty, then counts the lines
validate_file() {
    local filename="$1"

    # check file exists
    if [[ ! -f "$filename" ]]; then
        log "ERROR: $filename does not exist."
        exit 1
    fi

    # checks file is not empty
    local size
    size=$(wc -c < "$filename")  # wc -c counts bytes
    if [[ "$size" -eq 0 ]]; then
        log "ERROR: $filename is empty."
        exit 1
    fi

    # count the lines
    local lines
    lines=$(wc -l < "$filename")  # wc -l counts lines

    log "VALID: $filename — $lines lines, $size bytes."
}

# backs up file
backup_file() {
    local filename="$1"
    mkdir -p "$BACKUP_DIR"
    cp "$filename" "$BACKUP_DIR/$filename.bak"
    log "BACKUP: $filename saved to $BACKUP_DIR/$filename.bak"
}

# runs functions to download
log "===== Starting download pipeline ====="

download_file "$JULY_URL" "$JULY_FILE"
validate_file "$JULY_FILE"
backup_file "$JULY_FILE"

download_file "$AUG_URL" "$AUG_FILE"
validate_file "$AUG_FILE"
backup_file "$AUG_FILE"

log "===== All downloads complete and validated! ====="
