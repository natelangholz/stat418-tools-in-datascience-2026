#!/bin/bash
set -euo pipefail

LOGFILE="pipeline.log"

DATA_DIR="data"
OUT_DIR="output"

mkdir -p "$DATA_DIR" "$OUT_DIR"

########################################
# Logging helper
########################################
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOGFILE"
}

########################################
# Cleanup function
########################################
cleanup() {
  log "Cleaning temporary files..."
  rm -f /tmp/nasa_*.txt 2>/dev/null || true
  log "Cleanup complete."
}

trap cleanup EXIT

########################################
# Step runner
########################################
run_step() {
  local name="$1"
  local cmd="$2"

  log "----------------------------------------"
  log "Starting: $name"
  log "Command: $cmd"

  if eval "$cmd"; then
    log "SUCCESS: $name completed"
  else
    log "ERROR: $name failed"
    exit 1
  fi
}

########################################
# Pipeline start
########################################

log "NASA Log Processing Pipeline Started"

########################################
# 1. Download data
########################################
run_step "Download Data" "bash ./download_data.sh"

########################################
# 2. Analyze logs
########################################
run_step "Analyze Logs" "bash ./analyze_logs.sh data/NASA_Jul95.log data/NASA_Aug95.log"

########################################
# 3. Generate report
########################################
run_step "Generate Report" "bash ./generate_report.sh data/NASA_Jul95.log data/NASA_Aug95.log"

########################################
# Final message
########################################
log "----------------------------------------"
log "Pipeline complete!"
log "Report generated: REPORT.md"
log "Analysis files: $OUT_DIR/"
log "Logs saved: $LOGFILE"
