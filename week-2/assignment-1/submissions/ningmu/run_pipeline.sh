#!/bin/bash
# run_pipeline.sh - Master script for NASA log-analysis assignment.
# Runs:
#   1. download_data.sh     (download + validate + backup)
#   2. analyze_logs.sh      (per-file analysis, saved to logs/)
#   3. generate_report.sh   (build final REPORT.md)
# Usage: ./run_pipeline.sh

set -euo pipefail
export LC_ALL=C

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PIPELINE_LOG="pipeline.log"
ANALYSIS_DIR="analysis"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$PIPELINE_LOG"
}

fail() {
  log "ERROR: $1"
  exit 1
}

cleanup() {
  # Remove the intermediate analysis/ folder, but keep REPORT.md & logs.
  # Ignore filesystem errors so the pipeline still exits cleanly.
  if [[ -d "$ANALYSIS_DIR" ]]; then
    log "Cleaning up intermediate files in $ANALYSIS_DIR/"
    rm -rf "$ANALYSIS_DIR" 2>/dev/null || true
  fi
}
trap cleanup EXIT

log "=== Pipeline start ==="

# --- Stage 1: download ------------------------------------------------------
log "Stage 1/3: downloading data"
if [[ -f data/NASA_Jul95.log && -f data/NASA_Aug95.log ]]; then
  log "Data already present, skipping download."
else
  ./download_data.sh || fail "download_data.sh failed"
fi
log "Stage 1 complete."

# --- Stage 2: analyze -------------------------------------------------------
log "Stage 2/3: analyzing logs"
mkdir -p "$ANALYSIS_DIR"

./analyze_logs.sh data/NASA_Jul95.log > "$ANALYSIS_DIR/jul_analysis.txt" \
  || fail "analyze_logs.sh failed on July log"
log "  July analysis saved to $ANALYSIS_DIR/jul_analysis.txt"

./analyze_logs.sh data/NASA_Aug95.log > "$ANALYSIS_DIR/aug_analysis.txt" \
  || fail "analyze_logs.sh failed on August log"
log "  August analysis saved to $ANALYSIS_DIR/aug_analysis.txt"

log "Stage 2 complete."

# --- Stage 3: generate report ----------------------------------------------
log "Stage 3/3: generating report"
./generate_report.sh data/NASA_Jul95.log data/NASA_Aug95.log REPORT.md \
  || fail "generate_report.sh failed"
log "REPORT.md generated."

log "=== Pipeline complete ==="
echo
echo "Outputs:"
echo "  - data/NASA_Jul95.log, data/NASA_Aug95.log"
echo "  - backup/NASA_Jul95.log.bak, backup/NASA_Aug95.log.bak"
echo "  - REPORT.md"
echo "  - download.log, pipeline.log"
