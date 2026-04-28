#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="logs"
PIPELINE_LOG="$LOG_DIR/pipeline.log"
DATA_DIR="data"

mkdir -p "$LOG_DIR"

timestamp() { date "+%Y-%m-%d %H:%M:%S"; }

log() {
  local msg="[$(timestamp)] $1"
  echo "$msg" | tee -a "$PIPELINE_LOG"
}

step() {
  echo ""
  echo "========================================="
  echo "  $1"
  echo "========================================="
  log "STEP: $1"
}

fail() {
  log "FATAL: $1"
  echo "Pipeline failed. Check $PIPELINE_LOG for details." >&2
  exit 1
}

log "Pipeline started"

step "1/4  Downloading data"
if bash download_data.sh; then
  log "Download completed"
else
  fail "download_data.sh failed"
fi

step "2/4  Validating downloaded files"
for logfile in "$DATA_DIR/NASA_Jul95.log" "$DATA_DIR/NASA_Aug95.log"; do
  if [[ ! -f "$logfile" ]]; then
    fail "Missing file after download: $logfile"
  fi
  lines=$(wc -l < "$logfile")
  bytes=$(wc -c < "$logfile")
  log "Validated $logfile | lines=$lines bytes=$bytes"
  if [[ "$lines" -lt 100000 ]]; then
    fail "$logfile looks too small (only $lines lines) — download may be incomplete"
  fi
done
log "Validation passed"

step "3/4  Analyzing logs"
if bash analyze_logs.sh "$DATA_DIR/NASA_Jul95.log" "$DATA_DIR/NASA_Aug95.log"; then
  log "Analysis completed"
else
  fail "analyze_logs.sh failed"
fi

for result in analysis/NASA_Jul95_analysis.txt analysis/NASA_Aug95_analysis.txt; do
  if [[ ! -f "$result" ]]; then
    fail "Expected analysis output not found: $result"
  fi
  log "Found: $result"
done

step "4/4  Generating report"
if bash generate_report.sh; then
  log "Report generation completed"
else
  fail "generate_report.sh failed"
fi

if [[ ! -f "REPORT.md" ]]; then
  fail "REPORT.md was not created"
fi

log "Cleaning up temporary files"
rm -f "$DATA_DIR"/*.gz 2>/dev/null || true

echo ""
echo "========================================="
echo "  Pipeline complete"
echo "========================================="
log "Pipeline finished successfully"
echo ""
echo "Outputs:"
echo "  analysis/NASA_Jul95_analysis.txt"
echo "  analysis/NASA_Aug95_analysis.txt"
echo "  REPORT.md"
echo "  $PIPELINE_LOG"
