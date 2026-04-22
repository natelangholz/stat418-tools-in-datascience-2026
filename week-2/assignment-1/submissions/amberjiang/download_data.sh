#!/bin/bash
# download_data.sh - Download NASA log files

set -euo pipefail

# Log function for logging operations with timestamps
log() {
	echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Error exit function for handling download errors
error_exit() {
	log "ERROR: $1"
	exit 1
}

log "Downloading NASA web server logs..."

# Download July log
curl -s https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log > NASA_Jul95.log || error_exit "Failed to download data"
JUL=NASA_Jul95.log
log "Downloaded NASA_Jul95.log"

# Download August log
curl -s https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log > NASA_Aug95.log || error_exit "Failed to download data"
AUG=NASA_Aug95.log
log "Downloaded NASA_Aug95.log"

# Validate function to check downloaded file exists and check file size and line count
validate() {
  [[ -f "$1" ]] || error_exit "$1 was not created"

  local size=$(wc -c < "$1")
  local lines=$(wc -l < "$1")

  [[ "$size" -gt 0 ]] || error_exit "$1 is empty (0 bytes)"
  [[ "$lines" -gt 0 ]] || error_exit "$1 has 0 lines"

  log "Validated $1: $size bytes, $lines lines"
}

log "Validating both downloads..."
validate $JUL
validate $AUG

# Backup creation function
backup(){
	if [[ -f "$1" ]]; then
		cp "$1" "${1}.bak"
	log "Created backup of $1: ${1}.bak"
	fi
}

log "Creating backups..."
backup $JUL
backup $AUG

