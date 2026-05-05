#!/bin/bash
set -u

LOG_DIR="logs"
PIPELINE_LOG="$LOG_DIR/pipeline.log"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$PIPELINE_LOG"
}

cleanup() {
  log "Cleaning up temporary files..."
  rm -f *.tmp
  log "Cleanup complete"
}

run_step() {
  local script_name="$1"
  local step_name="$2"

  if [[ ! -f "$script_name" ]]; then
    log "ERROR: $script_name not found"
    exit 1
  fi

  if [[ ! -x "$script_name" ]]; then
    chmod +x "$script_name"
  fi

  log "Starting $step_name..."
  if ./"$script_name"; then
    log "$step_name completed successfully"
  else
    log "ERROR: $step_name failed"
    cleanup
    exit 1
  fi
}

log "Starting full NASA log analysis pipeline"

run_step "download_data.sh" "Step 1 - Data download"
run_step "analyze_logs.sh" "Step 2 - Data analysis"
run_step "generate_report.sh" "Step 3 - Report generation"

if [[ -f "REPORT.md" ]]; then
  log "Final report generated: REPORT.md"
else
  log "ERROR: REPORT.md was not created"
  cleanup
  exit 1
fi

cleanup

log "Pipeline completed successfully"