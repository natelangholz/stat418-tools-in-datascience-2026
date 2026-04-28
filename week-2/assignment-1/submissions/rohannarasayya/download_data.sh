#!/bin/bash
# download_data.sh - Download and validate NASA web server log files
set -euo pipefail

# Minimum acceptable thresholds (NASA Jul95 ~1.9M lines, Aug95 ~1.5M lines)
MIN_LINES_JUL=1000000
MIN_LINES_AUG=1000000
MIN_BYTES=50000000   # 50 MB — both files are >100 MB each

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

download_and_validate() {
    local url="$1"
    local outfile="$2"
    local min_lines="$3"

    log "Downloading $outfile from $url ..."
    if ! curl -s --fail "$url" > "$outfile"; then
        log "ERROR: curl failed for $url"
        exit 1
    fi
    log "Downloaded $outfile"

    # File size validation
    local bytes
    bytes=$(wc -c < "$outfile")
    log "File size: $bytes bytes"
    if [ "$bytes" -lt "$MIN_BYTES" ]; then
        log "ERROR: $outfile is too small ($bytes bytes < $MIN_BYTES minimum). Download may be incomplete."
        exit 2
    fi
    log "File size OK ($bytes bytes)"

    # Line count validation
    local lines
    lines=$(wc -l < "$outfile")
    log "Line count: $lines lines"
    if [ "$lines" -lt "$min_lines" ]; then
        log "ERROR: $outfile has too few lines ($lines < $min_lines minimum). Download may be truncated."
        exit 3
    fi
    log "Line count OK ($lines lines)"

    # Create .bak backup copy
    cp "$outfile" "${outfile}.bak"
    log "Backup created: ${outfile}.bak"
}

log "=== Starting NASA log file download ==="

download_and_validate \
    "https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log" \
    "NASA_Jul95.log" \
    "$MIN_LINES_JUL"

download_and_validate \
    "https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log" \
    "NASA_Aug95.log" \
    "$MIN_LINES_AUG"

log "=== Download complete! Both files validated and backed up. ==="
