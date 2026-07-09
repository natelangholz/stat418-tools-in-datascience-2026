LOG_FILE="download.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting download of NASA web server logs"

log "Downloading NASA_Jul95.log"
curl -s https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log > NASA_Jul95.log
log "Download complete: NASA_Jul95.log"

log "Downloading NASA_Aug95.log"
curl -s https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log > NASA_Aug95.log
log "Download complete: NASA_Aug95.log"

# Validate downloads
validate_file() {
    local file=$1
    local min_size_mb=$2
    local min_lines=$3

    if [ ! -f "$file" ]; then
        log "ERROR: $file not found"
        return 1
    fi

    local size_bytes
    size_bytes=$(wc -c < "$file")
    local size_mb=$(( size_bytes / 1024 / 1024 ))
    if [ "$size_mb" -lt "$min_size_mb" ]; then
        log "ERROR: $file too small (${size_mb}MB < ${min_size_mb}MB expected)"
        return 1
    fi

    local lines
    lines=$(wc -l < "$file")
    if [ "$lines" -lt "$min_lines" ]; then
        log "ERROR: $file has too few lines ($lines < $min_lines expected)"
        return 1
    fi

    log "OK: $file — ${size_mb}MB, $lines lines"
}

log "Validating downloads"
validate_file NASA_Jul95.log 100 1000000
validate_file NASA_Aug95.log 100 1000000

# Backup original files
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp NASA_Jul95.log NASA_Aug95.log "$BACKUP_DIR/"
log "Backup created: $BACKUP_DIR/"

log "All done"
