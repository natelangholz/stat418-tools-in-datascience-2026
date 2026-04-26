#!/usr/bin/env bash
# download_data.sh
# -----------------------------------------------------------------------------
# Part 1: Data Acquisition and Validation
#
# Downloads NASA web server logs (July & August 1995), validates the downloads,
# creates a backup of the original files, and logs every operation with a
# timestamp so failures can be diagnosed after the fact.
#
# Usage:
#   ./download_data.sh            # downloads into ./data
#   ./download_data.sh /tmp/nasa  # downloads into /tmp/nasa
# -----------------------------------------------------------------------------

set -euo pipefail

# --- Config ------------------------------------------------------------------

readonly DATA_DIR="${1:-./data}"
readonly BACKUP_DIR="${DATA_DIR}/backup"
readonly LOG_DIR="${DATA_DIR}/logs"
readonly RUN_LOG="${LOG_DIR}/download_$(date +%Y%m%d_%H%M%S).log"

# Minimum size (bytes) and line count we expect to see for a valid download.
# The original July and August files are ~20MB / ~180MB respectively, so
# anything under 1MB almost certainly means the download was truncated.
readonly MIN_BYTES=1000000
readonly MIN_LINES=100000

# URL (name, url) pairs.
readonly URLS=(
  "NASA_Jul95.log|https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log"
  "NASA_Aug95.log|https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log"
)

# --- Helpers -----------------------------------------------------------------

log() {
  # Log a message with ISO-8601 timestamp to both stdout and the run log.
  local ts
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  local msg="[${ts}] $*"
  echo "${msg}"
  echo "${msg}" >> "${RUN_LOG}"
}

die() {
  log "ERROR: $*"
  exit 1
}

ensure_dirs() {
  mkdir -p "${DATA_DIR}" "${BACKUP_DIR}" "${LOG_DIR}"
  # touch run log so later `log` calls succeed even before first real write.
  : > "${RUN_LOG}"
}

download_one() {
  # Downloads a single file with retries and a progress bar.
  local name="$1"
  local url="$2"
  local dest="${DATA_DIR}/${name}"
  local tmp="${dest}.part"

  log "Downloading ${name} from ${url}"

  # -f       fail on HTTP errors (e.g., 404 → non-zero exit)
  # -L       follow redirects
  # --retry  retry on transient errors
  if ! curl -fL --retry 3 --retry-delay 5 --retry-connrefused \
            --connect-timeout 30 --max-time 1800 \
            --progress-bar \
            -o "${tmp}" "${url}"; then
    rm -f "${tmp}"
    return 1
  fi

  mv "${tmp}" "${dest}"
  log "Saved to ${dest}"
  return 0
}

validate_one() {
  # Validates a single file: exists, big enough, plausible line count, and
  # at least one line matches the expected common-log format.
  local name="$1"
  local path="${DATA_DIR}/${name}"

  [[ -f "${path}" ]] || { log "VALIDATE FAIL: ${name} does not exist"; return 1; }

  local size
  size="$(wc -c < "${path}" | tr -d ' ')"
  if (( size < MIN_BYTES )); then
    log "VALIDATE FAIL: ${name} is only ${size} bytes (< ${MIN_BYTES})"
    return 1
  fi

  local lines
  lines="$(wc -l < "${path}" | tr -d ' ')"
  if (( lines < MIN_LINES )); then
    log "VALIDATE FAIL: ${name} has only ${lines} lines (< ${MIN_LINES})"
    return 1
  fi

  # Sanity check: at least one of the first 20 lines must look like a
  # Common Log Format entry (host ... [date] "METHOD url PROTO" status bytes).
  if ! head -20 "${path}" | grep -Eq '\[[0-9]{2}/[A-Za-z]{3}/[0-9]{4}.*\] "[A-Z]+ .*" [0-9]+ '; then
    log "VALIDATE FAIL: ${name} does not appear to be in Common Log Format"
    return 1
  fi

  log "VALIDATE OK: ${name}  size=${size} bytes  lines=${lines}"
  return 0
}

backup_one() {
  # Gzip-compressed backup alongside original.
  local name="$1"
  local src="${DATA_DIR}/${name}"
  local bak="${BACKUP_DIR}/${name}.$(date +%Y%m%d).gz"

  if [[ -f "${bak}" ]]; then
    log "Backup already exists: ${bak}"
    return 0
  fi

  log "Backing up ${name} -> ${bak}"
  gzip -c "${src}" > "${bak}"
  log "Backup complete ($(wc -c < "${bak}" | tr -d ' ') bytes compressed)"
}

# --- Main --------------------------------------------------------------------

main() {
  ensure_dirs
  log "download_data.sh starting (data dir = ${DATA_DIR})"

  local failed=0
  for entry in "${URLS[@]}"; do
    local name="${entry%%|*}"
    local url="${entry##*|}"
    local dest="${DATA_DIR}/${name}"

    # Skip re-download if we already have a valid copy — saves bandwidth
    # when the script is re-run.
    if [[ -f "${dest}" ]] && validate_one "${name}" >/dev/null 2>&1; then
      log "Skipping download: ${name} already present and valid"
    else
      if ! download_one "${name}" "${url}"; then
        log "Download failed for ${name}"
        failed=$((failed + 1))
        continue
      fi
      if ! validate_one "${name}"; then
        log "Validation failed for ${name}"
        failed=$((failed + 1))
        continue
      fi
    fi

    backup_one "${name}"
  done

  if (( failed > 0 )); then
    die "${failed} file(s) failed to download / validate. See ${RUN_LOG}"
  fi

  log "download_data.sh complete. Run log: ${RUN_LOG}"
}

main "$@"
