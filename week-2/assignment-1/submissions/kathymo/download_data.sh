# Download NASA log files

# Permissions: chmod +x analyze_logs.sh
# to run: bash download_data.sh

#!/bin/bash
set -euo pipefail

# Define the log file
LOG_FILE="setup.log"

# Create a function to handle timestamps and logging
log_event() {
    local message="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $message" | tee -a "$LOG_FILE"
}

# Downloading files
log_event "Started downloading NASA web server logs..."

# Download July Log
if curl -sf https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log -o NASA_Jul95.log; then
    log_event "Finished downloading NASA_Jul95.log"
else
    log_event "ERROR: Download failed for NASA_Jul95.log"
    exit 1
fi

# Download August Log
if curl -sf https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log -o NASA_Aug95.log; then
    log_event "Finished downloading NASA_Aug95.log"
else
    log_event "ERROR: Download failed for NASA_Aug95.log"
    exit 1
fi

# Validation
log_event "Started validating files..."

JUL_SIZE=$(wc -c < NASA_Jul95.log | awk '{print $1}')
JUL_LINES=$(wc -l < NASA_Jul95.log | awk '{print $1}')
log_event "NASA_Jul95.log size: $JUL_SIZE bytes, $JUL_LINES lines"

AUG_SIZE=$(wc -c < NASA_Aug95.log | awk '{print $1}')
AUG_LINES=$(wc -l < NASA_Aug95.log | awk '{print $1}')
log_event "NASA_Aug95.log size: $AUG_SIZE bytes, $AUG_LINES lines"

log_event "Finished validation"

# Backups
log_event "Started creating backups..."

if [ -f "backups/NASA_Jul95.log.bak" ] && [ -f "backups/NASA_Aug95.log.bak" ]; then
    log_event "Backup already exists. Skipping this step."
else
    mkdir -p backups
    cp NASA_Jul95.log backups/NASA_Jul95.log.bak
    cp NASA_Aug95.log backups/NASA_Aug95.log.bak
    log_event "Finished creating backups"
fi

log_event "Process complete"