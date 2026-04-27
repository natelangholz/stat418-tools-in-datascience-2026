
set -euo pipefail

DATA_DIR="${1:-data}"
LOG_DIR="${2:-logs}"
mkdir -p "$DATA_DIR" "$LOG_DIR" "$DATA_DIR/original_backups"

timestamp() { date "+%Y-%m-%d %H:%M:%S"; }
log() { echo "[$(timestamp)] $*" | tee -a "$LOG_DIR/download.log"; }

download_file() {
  local url="$1"
  local out="$2"

  log "Downloading $out from $url"
  if ! curl -fL --retry 3 --connect-timeout 20 --silent --show-error "$url" -o "$DATA_DIR/$out"; then
    log "ERROR: failed to download $out"
    return 1
  fi

  if [[ ! -s "$DATA_DIR/$out" ]]; then
    log "ERROR: downloaded file $out is empty"
    return 1
  fi

  local line_count byte_count
  line_count=$(wc -l < "$DATA_DIR/$out")
  byte_count=$(wc -c < "$DATA_DIR/$out")

  log "Validated $out: ${line_count} lines, ${byte_count} bytes"
  cp "$DATA_DIR/$out" "$DATA_DIR/original_backups/${out}.bak"
  log "Created backup: $DATA_DIR/original_backups/${out}.bak"
}

main() {
  log "Starting download pipeline"
  download_file "https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log" "NASA_Jul95.log"
  download_file "https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log" "NASA_Aug95.log"
  log "All downloads complete"
}

main "$@"
