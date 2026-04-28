#!/bin/bash
# hw1-starter.sh - Download NASA log files

set -euo pipefail

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

echo "Downloading NASA web server logs..."
log "Downloading NASA web server logs..."

# Download July log
curl -s https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log > NASA_Jul95.log || {
    log "Error: NASA_Jul95.log not found"
    exit 1
}
echo "Downloaded NASA_Jul95.log"
log "Downloaded NASA_Jul95.log"

echo "Download complete!"

# Validate July log
if [ ! -f NASA_Jul95.log ]; then
    log "Error: NASA_Jul95.log not found"
    exit 1
fi

wc -l NASA_Jul95.log
ls -lh NASA_Jul95.log

# Download August log
curl -s https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log > NASA_Aug95.log || {
    log "Error: NASA_AUg95.log not found"
    exit 1
}
echo "Downloaded NASA_Aug95.log"
log "Downloaded NASA_Aug95.log"

echo "Download complete!"

# Validate August log
if [ ! -f NASA_Aug95.log ]; then
    log "Error: NASA_Aug95.log not found"
    exit 1
fi

wc -l NASA_Aug95.log
ls -lh NASA_Aug95.log

## Download Backup July log
cp NASA_Jul95.log NASA_Jul95_backup.log
echo "Downloaded NASA_Jul95_backup.log"
log "Downloaded NASA_Jul95_backup.log"

# # Download Backup August log
cp NASA_Aug95.log NASA_Aug95_backup.log
echo "Downloaded NASA_Aug95_backup.log"
log "Downloaded NASA_Aug95_backup.log"

echo "Download backup complete!"
log "Completed Successfully"