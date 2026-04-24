#!/bin/bash
# hw1-starter.sh - Download NASA log files

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $@"
}

log "Downloading NASA web server logs..."

# backup existing files
if [ -e NASA_Jul95.log ]; then
    mv -n NASA_Jul95.log NASA_Jul95.log.bak
    log "Existing NASA_Jul95.log renamed to NASA_Jul95.log.bak"
fi

if [ -e NASA_Aug95.log ]; then
    mv -n NASA_Aug95.log NASA_Aug95.log.bak
    log "Existing NASA_Aug95.log renamed to NASA_Aug95.log.bak"
fi

# Download July log
if curl -sL --fail --retry 5 --retry-all-errors -o NASA_Jul95.log "https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log"; then
    log "Downloaded NASA_Jul95.log"
else
    log "Failed to download NASA_Jul95.log"
    exit 1
fi


log "Line count for July log: $(wc -l NASA_Jul95.log | awk '{print $1}')"
log "Byte count for July log: $(wc -c NASA_Jul95.log | awk '{print $1}')"


# Download August log
if curl -sL --fail --retry 5 --retry-all-errors -o NASA_Aug95.log "https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log"; then
    log "Downloaded NASA_Aug95.log"
else
    log "Failed to download NASA_Aug95.log"
    exit 1
fi

log "Line count for August log: $(wc -l NASA_Aug95.log | awk '{print $1}')"
log "Byte count for August log: $(wc -c NASA_Aug95.log | awk '{print $1}')"

log "Download complete!"