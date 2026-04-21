#!/bin/bash
# run_pipeline.sh - Master pipeline: download → analyze → report → cleanup
# Usage: ./run_pipeline.sh [--skip-download] [--keep-tmp]

set -euo pipefail

SKIP_DOWNLOAD=false
KEEP_TMP=false

for arg in "$@"; do
    case "$arg" in
        --skip-download) SKIP_DOWNLOAD=true ;;
        --keep-tmp)      KEEP_TMP=true ;;
        *) echo "Unknown option: $arg"; exit 1 ;;
    esac
done

JUL_LOG="data/NASA_Jul95.log"
AUG_LOG="data/NASA_Aug95.log"
ANALYSIS_DIR="analysis"
LOG_FILE="pipeline.log"

# ── Helpers ────────────────────────────────────────────────────────────────
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

die() { log "FATAL: $*"; exit 1; }

run_step() {
    local step="$1"; shift
    log "Starting: $step"
    if "$@"; then
        log "Done:     $step"
    else
        die "$step failed (exit $?)"
    fi
}

# ── Setup ──────────────────────────────────────────────────────────────────
mkdir -p "$ANALYSIS_DIR"
log "=== NASA Log Pipeline ==="
log "Working directory: $(pwd)"

# ── Step 1: Download ───────────────────────────────────────────────────────
if $SKIP_DOWNLOAD; then
    log "Skipping download (--skip-download)"
    [ -f "$JUL_LOG" ] || die "Jul log not found at $JUL_LOG — remove --skip-download"
    [ -f "$AUG_LOG" ] || die "Aug log not found at $AUG_LOG — remove --skip-download"
else
    run_step "Download data" bash download_data.sh
fi

# ── Step 2: Analyze July ──────────────────────────────────────────────────
run_step "Analyze July log" bash analyze_logs.sh "$JUL_LOG" \
    | tee "$ANALYSIS_DIR/analysis_july.txt"

# ── Step 3: Analyze August ───────────────────────────────────────────────
run_step "Analyze August log" bash analyze_logs.sh "$AUG_LOG" \
    | tee "$ANALYSIS_DIR/analysis_august.txt"

# ── Step 4: Generate report ───────────────────────────────────────────────
run_step "Generate report" bash generate_report.sh \
    "$ANALYSIS_DIR/analysis_july.txt" \
    "$ANALYSIS_DIR/analysis_august.txt"

# ── Step 5: Cleanup temp files ────────────────────────────────────────────
if $KEEP_TMP; then
    log "Keeping temporary files (--keep-tmp)"
else
    log "Cleaning up temporary files ..."
    rm -f data/*.tmp 2>/dev/null || true
    log "Cleanup done"
fi

# ── Summary ───────────────────────────────────────────────────────────────
log "=== Pipeline complete ==="
log "Outputs:"
log "  Analysis (July)   : $ANALYSIS_DIR/analysis_july.txt"
log "  Analysis (August) : $ANALYSIS_DIR/analysis_august.txt"
log "  Report            : REPORT.md"
log "  Pipeline log      : $LOG_FILE"
