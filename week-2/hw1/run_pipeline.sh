#!/bin/bash
# run_pipeline.sh - Master pipeline script that runs all steps in order

# --- Configuration ---
JULY_LOG="NASA_Jul95.log"
AUG_LOG="NASA_Aug95.log"
JULY_RESULTS="july_results.txt"
AUG_RESULTS="aug_results.txt"

# --- Helper: print progress messages with timestamp ---
progress() {
    echo ""
    echo "================================================"
    echo " [$(date '+%H:%M:%S')] $1"
    echo "================================================"
}

# --- Helper: check if a previous step failed ---
check_success() {
    if [[ $? -ne 0 ]]; then
        echo "ERROR: $1 failed. Stopping pipeline."
        exit 1
    fi
}

# -------------------------------------------------------
# STEP 1: Download data
# -------------------------------------------------------
progress "STEP 1: Downloading log files..."

if [[ -f "$JULY_LOG" && -f "$AUG_LOG" ]]; then
    echo "Log files already exist — skipping download."
    echo "Delete NASA_Jul95.log and NASA_Aug95.log to re-download."
else
    bash download_data.sh
    check_success "download_data.sh"
fi

# -------------------------------------------------------
# STEP 2: Analyze July
# -------------------------------------------------------
progress "STEP 2: Analyzing July logs (this will take ~30 mins)..."

bash analyze_logs.sh "$JULY_LOG" > "$JULY_RESULTS" 2>&1
check_success "analyze_logs.sh (July)"
echo "July analysis saved to $JULY_RESULTS"

# -------------------------------------------------------
# STEP 3: Analyze August
# -------------------------------------------------------
progress "STEP 3: Analyzing August logs (this will take ~30 mins)..."

bash analyze_logs.sh "$AUG_LOG" > "$AUG_RESULTS" 2>&1
check_success "analyze_logs.sh (August)"
echo "August analysis saved to $AUG_RESULTS"

# -------------------------------------------------------
# STEP 4: Generate report
# -------------------------------------------------------
progress "STEP 4: Generating report..."

bash generate_report.sh
check_success "generate_report.sh"

# -------------------------------------------------------
# STEP 5: Clean up temporary files
# -------------------------------------------------------
progress "STEP 5: Cleaning up..."

# Remove test sample if it exists
if [[ -f "test_sample.log" ]]; then
    rm test_sample.log
    echo "Removed test_sample.log"
fi

echo "Cleanup complete."

# -------------------------------------------------------
# DONE
# -------------------------------------------------------
progress "PIPELINE COMPLETE!"
echo ""
echo "Output files:"
echo "  - july_results.txt   (July analysis)"
echo "  - aug_results.txt    (August analysis)"
echo "  - REPORT.md          (Final report)"
echo "  - download_log.txt   (Download log)"
echo "  - backups/           (Original log backups)"
echo ""
echo "To view your report:"
echo "  explorer.exe REPORT.md"
