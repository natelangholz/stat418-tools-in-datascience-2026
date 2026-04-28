#!/bin/bash
# run_pipeline.sh - Master pipeline for NASA web server log analysis
# Usage: ./run_pipeline.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
step_start() {
    # $1 = step label  — printed to terminal; sets global _STEP_START
    echo ""
    echo "$1"
    _STEP_START=$(date +%s)
}

step_end() {
    local elapsed=$(( $(date +%s) - _STEP_START ))
    echo "    Done in ${elapsed}s"
}

die() {
    echo "[ERROR] $1" >&2
    exit 1
}

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
PIPELINE_START=$(date +%s)
echo "============================================================"
echo "  NASA Log Analysis Pipeline"
echo "  Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

# ---------------------------------------------------------------------------
# Step 1: Download and validate log files
# ---------------------------------------------------------------------------
step_start "[Step 1/4] Downloading and validating log files..."
bash "$SCRIPT_DIR/download_data.sh" \
    || die "Download failed"
step_end

# ---------------------------------------------------------------------------
# Step 2: Analyze July logs
# ---------------------------------------------------------------------------
step_start "[Step 2/4] Analyzing July logs..."
bash "$SCRIPT_DIR/analyze_logs.sh" "$SCRIPT_DIR/NASA_Jul95.log" \
    > "$SCRIPT_DIR/analysis_jul.tmp" 2>&1 \
    || die "Analysis failed for July"
echo "    Lines processed: $(wc -l < "$SCRIPT_DIR/NASA_Jul95.log")"
step_end

# ---------------------------------------------------------------------------
# Step 3: Analyze August logs
# ---------------------------------------------------------------------------
step_start "[Step 3/4] Analyzing August logs..."
bash "$SCRIPT_DIR/analyze_logs.sh" "$SCRIPT_DIR/NASA_Aug95.log" \
    > "$SCRIPT_DIR/analysis_aug.tmp" 2>&1 \
    || die "Analysis failed for August"
echo "    Lines processed: $(wc -l < "$SCRIPT_DIR/NASA_Aug95.log")"
step_end

# ---------------------------------------------------------------------------
# Step 4: Generate report
# ---------------------------------------------------------------------------
step_start "[Step 4/4] Generating report..."
bash "$SCRIPT_DIR/generate_report.sh" \
    || die "Report generation failed"
echo "    Report: $SCRIPT_DIR/REPORT.md ($(wc -l < "$SCRIPT_DIR/REPORT.md") lines)"
step_end

# ---------------------------------------------------------------------------
# Cleanup .tmp files
# ---------------------------------------------------------------------------
echo ""
echo "[Cleanup] Removing temporary files..."
tmp_count=0
for f in "$SCRIPT_DIR"/*.tmp; do
    [[ -e "$f" ]] || continue
    rm -f "$f"
    echo "    Removed: $(basename "$f")"
    (( tmp_count++ )) || true
done
[[ $tmp_count -eq 0 ]] && echo "    (no .tmp files found)"

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
PIPELINE_END=$(date +%s)
TOTAL=$(( PIPELINE_END - PIPELINE_START ))
echo ""
echo "============================================================"
echo "  Pipeline complete! See REPORT.md for results."
echo "  Total time: ${TOTAL}s"
echo "============================================================"
