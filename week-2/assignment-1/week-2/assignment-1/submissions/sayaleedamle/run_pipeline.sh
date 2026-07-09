#!/bin/bash
# run_pipeline.sh - Master pipeline: download → analyse → report → cleanup
# Usage: ./run_pipeline.sh [--skip-download]

set -uo pipefail   # -e intentionally omitted; each stage error is handled explicitly

# ── Configuration ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PIPELINE_LOG="$SCRIPT_DIR/pipeline.log"
REPORT="$SCRIPT_DIR/REPORT.md"
TMP_FILES=()          # accumulates temp files to clean up at end
STAGE_PASS=()
STAGE_FAIL=()
SKIP_DOWNLOAD=false

[ "${1:-}" = "--skip-download" ] && SKIP_DOWNLOAD=true

# ── Logging helpers ───────────────────────────────────────────────────────────
ts()     { date '+%Y-%m-%d %H:%M:%S'; }
log()    { echo "[$(ts)] $*" | tee -a "$PIPELINE_LOG"; }
log_ok() { echo "[$(ts)] ✓  $*" | tee -a "$PIPELINE_LOG"; }
log_err(){ echo "[$(ts)] ✗  $*" | tee -a "$PIPELINE_LOG" >&2; }

divider() { echo "────────────────────────────────────────────────────" | tee -a "$PIPELINE_LOG"; }

# ── Stage runner ──────────────────────────────────────────────────────────────
# Usage: run_stage <stage_name> <command> [args…]
# Streams command output to log; records pass/fail; never exits early.
run_stage() {
    local name="$1"; shift
    divider
    log "STAGE: $name"

    # Run in a subshell so set -e inside child scripts doesn't kill us;
    # pipe SIGPIPE (141) is treated as success since head/sort can close pipes early.
    local rc=0
    { "$@" 2>&1; rc=$?; } | tee -a "$PIPELINE_LOG" || true
    [ $rc -eq 141 ] && rc=0   # suppress SIGPIPE — harmless pipe close from head/sort

    if [ $rc -eq 0 ]; then
        log_ok "$name completed successfully"
        STAGE_PASS+=("$name")
    else
        log_err "$name FAILED (exit code $rc)"
        STAGE_FAIL+=("$name")
    fi
    return $rc
}

# ── Cleanup tracker ───────────────────────────────────────────────────────────
track_tmp() { TMP_FILES+=("$@"); }

cleanup() {
    if [ ${#TMP_FILES[@]} -eq 0 ]; then
        log "No temporary files to remove."
        return
    fi
    log "Cleaning up ${#TMP_FILES[@]} temporary file(s)…"
    for f in "${TMP_FILES[@]}"; do
        if [ -e "$f" ]; then
            rm -rf "$f" && log "  removed: $f"
        fi
    done
}

# ── Pre-flight checks ─────────────────────────────────────────────────────────
: > "$PIPELINE_LOG"   # truncate/create log
divider
log "NASA Log Analysis Pipeline — started at $(ts)"
log "Working directory: $SCRIPT_DIR"
divider

required_scripts=(analyze_logs.sh generate_report.sh)
$SKIP_DOWNLOAD || required_scripts=(download_data.sh "${required_scripts[@]}")

for s in "${required_scripts[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$s" ]; then
        log_err "Required script not found: $s"
        exit 1
    fi
    chmod +x "$SCRIPT_DIR/$s"
done

# ── Stage 1: Download data ────────────────────────────────────────────────────
if $SKIP_DOWNLOAD; then
    log "Skipping download stage (--skip-download flag set)."
    for f in NASA_Jul95.log NASA_Aug95.log; do
        if [ ! -f "$SCRIPT_DIR/$f" ]; then
            log_err "$f not found and download was skipped — cannot continue."
            exit 1
        fi
    done
    STAGE_PASS+=("1. Download (skipped — files present)")
else
    run_stage "1. Download & validate data" bash "$SCRIPT_DIR/download_data.sh"
    # If download failed, abort — nothing else can run without log files
    if [ ${#STAGE_FAIL[@]} -gt 0 ]; then
        log_err "Download stage failed — aborting pipeline."
        cleanup
        exit 1
    fi
fi

# Track any backup directories for optional cleanup
for bk in "$SCRIPT_DIR"/backup_*/; do
    [ -d "$bk" ] && track_tmp "$bk"
done

# ── Stage 2: Analyse July log ─────────────────────────────────────────────────
JUL_RESULTS="$SCRIPT_DIR/results_july.txt"
track_tmp "$JUL_RESULTS"
run_stage "2. Analyse NASA_Jul95.log" bash -c \
    "bash '$SCRIPT_DIR/analyze_logs.sh' '$SCRIPT_DIR/NASA_Jul95.log' > '$JUL_RESULTS'"

# ── Stage 3: Analyse August log ───────────────────────────────────────────────
AUG_RESULTS="$SCRIPT_DIR/results_august.txt"
track_tmp "$AUG_RESULTS"
run_stage "3. Analyse NASA_Aug95.log" bash -c \
    "bash '$SCRIPT_DIR/analyze_logs.sh' '$SCRIPT_DIR/NASA_Aug95.log' > '$AUG_RESULTS'"

# ── Stage 4: Generate report ──────────────────────────────────────────────────
run_stage "4. Generate markdown report" bash "$SCRIPT_DIR/generate_report.sh"

# ── Stage 5: Cleanup ──────────────────────────────────────────────────────────
divider
log "STAGE: 5. Cleanup"
cleanup
STAGE_PASS+=("5. Cleanup")

# ── Final summary ─────────────────────────────────────────────────────────────
divider
log "PIPELINE SUMMARY"
log "Passed  (${#STAGE_PASS[@]}): ${STAGE_PASS[*]}"
if [ ${#STAGE_FAIL[@]} -gt 0 ]; then
    log_err "Failed  (${#STAGE_FAIL[@]}): ${STAGE_FAIL[*]}"
fi
divider

if [ ${#STAGE_FAIL[@]} -eq 0 ]; then
    log_ok "All stages passed."
    if [ -f "$REPORT" ]; then
        log_ok "Report: $REPORT"
        log    "  Size: $(wc -l < "$REPORT") lines"
    fi
    log "Full log: $PIPELINE_LOG"
    exit 0
else
    log_err "${#STAGE_FAIL[@]} stage(s) failed — check $PIPELINE_LOG for details."
    exit 1
fi
