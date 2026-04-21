#!/bin/bash
# download_data.sh - Download, validate, and back up NASA web server logs

set -euo pipefail

# ── Config ─────────────────────────────────────────────────────────────────
DATA_DIR="data"
BACKUP_DIR="data/backup"
LOG_FILE="pipeline.log"

JUL_URL="https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log"
AUG_URL="https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log"
JUL_FILE="$DATA_DIR/NASA_Jul95.log"
AUG_FILE="$DATA_DIR/NASA_Aug95.log"

MIN_LINES=100000   # sanity check: real files have ~1.8M lines each
MIN_BYTES=1000000

# ── Helpers ────────────────────────────────────────────────────────────────
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

download_file() {
    local url="$1" dest="$2" label="$3"
    log "Downloading $label ..."
    if ! curl --fail --silent --show-error --location -o "$dest" "$url"; then
        log "ERROR: Failed to download $label from $url"
        return 1
    fi
    log "Saved $label → $dest"
}

validate_file() {
    local file="$1" label="$2"

    if [ ! -f "$file" ]; then
        log "ERROR: $file does not exist"
        return 1
    fi

    local bytes
    bytes=$(wc -c < "$file")
    if [ "$bytes" -lt "$MIN_BYTES" ]; then
        log "ERROR: $label is too small ($bytes bytes) — download may be incomplete"
        return 1
    fi

    local lines
    lines=$(wc -l < "$file")
    if [ "$lines" -lt "$MIN_LINES" ]; then
        log "ERROR: $label has only $lines lines — expected at least $MIN_LINES"
        return 1
    fi

    log "Validated $label: $lines lines, $bytes bytes — OK"
}

backup_file() {
    local file="$1" label="$2"
    local dest="$BACKUP_DIR/$(basename "$file").bak"
    cp "$file" "$dest"
    log "Backup $label → $dest"
}

# ── Main ───────────────────────────────────────────────────────────────────
main() {
    log "=== NASA Log Download Pipeline ==="
    mkdir -p "$DATA_DIR" "$BACKUP_DIR"

    # Download
    download_file "$JUL_URL" "$JUL_FILE" "NASA_Jul95.log"
    download_file "$AUG_URL" "$AUG_FILE" "NASA_Aug95.log"

    # Validate
    validate_file "$JUL_FILE" "NASA_Jul95.log"
    validate_file "$AUG_FILE" "NASA_Aug95.log"

    # Backup originals
    backup_file "$JUL_FILE" "NASA_Jul95.log"
    backup_file "$AUG_FILE" "NASA_Aug95.log"

    log "=== Download complete ==="
}

main "$@"
