#!/bin/bash

# Pipeline Integration

# Handle errors
set -euo pipefail


# scripts
SCRIPT1="./download_data.sh"
SCRIPT2="./analyze_logs.sh"
SCRIPT3="./generate_report.sh"
REPORT="REPORT.md"
# temporary directory to run files
TEMP_DIR="./temp_run"
# name temp directory
mkdir -p "$TEMP_DIR"



# Provide progress updates
info() { echo -e "\033[1;34m[INFO]\033[0m $*"; }
ok() { echo -e "\033[1;32m[OK]\033[0m $*"; }
error() { echo -e "\033[1;31m[ERROR]\033[0m $*"; }
# errors 
trap 'error "Script failed on line $LINENO"; exit 1' ERR


# run pipeline
info "Step 1: Starting data download in $SCRIPT1..."
bash "$SCRIPT1" > "$TEMP_DIR/step1.out"
ok "Step 1: Data download complete."

info "Step 2: Starting log analysis in $SCRIPT2..."
bash "$SCRIPT2" > "$TEMP_DIR/step2.out"
ok "Step 2: Log analysis complete."

info "Step 3: Starting summary statistics in $SCRIPT3..."
bash "$SCRIPT3" > "$TEMP_DIR/step3.out"
ok "Step 3: Summary statistics complete."

# generate report
info "Generating final report: $REPORT..."

{
echo "# Final Report: Analysis of NASA Web Server Logs"
echo
echo "Generated on: $(date)"
echo
echo "## Step 1 Output"
echo '```'
cat "$TEMP_DIR/step1.out"
echo '```'
echo
echo "## Step 2 Output"
echo '```'
cat "$TEMP_DIR/step2.out"
echo '```'
echo
echo "## Step 3 Output"
echo '```'
cat "$TEMP_DIR/step3.out"
echo '```'
} > "$REPORT"

ok "Report generated"

# Part 5:Clean up temporary files
info "Clean up temporary files..."
rm -rf "$TEMP_DIR"
ok "Clean up complete."

info "All steps completed successfully."














