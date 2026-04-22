#!/bin/bash
# run_pipeline.sh
# Master pipeline script for Assignment 1

set -euo pipefail

echo "==============================="
echo " Starting Data Pipeline"
echo "==============================="


# --- Stage 1 ---
echo "[1/4] Fetching raw data and check required files"
echo "Checking that log files exist..."
bash download_data.sh

if [[ ! -f NASA_Jul95.log ]]; then
    echo "Error: NASA_Jul95.log not found"
    exit 1
fi

if [[ ! -f NASA_Aug95.log ]]; then
    echo "Error: NASA_Aug95.log not found"
    exit 1
fi

echo "Input files found."


# --- Stage 2 ---
echo "[2/4] Run analysis script..."
bash analyze_logs.sh
echo "Analysis complete"

# --- Stage 3 ---
echo "[3/4] Generate Report..."
bash generate_report.sh

if [ ! -f REPORT.md ]; then
    echo "Error: REPORT.md was not created. Stopping."
    exit 1
fi
echo "Report created successfully."

# --- Stage 4 ---
echo "[4/4] Clean up temporary files"
echo "Cleaning up temporary files..."
rm -f all_july_hosts.txt
rm -f all_aug_hosts.txt
rm -f july_response_code.txt
rm -f aug_response_code.txt
rm -f dates_present_aug.txt
rm -f all_dates_aug.txt

echo "Cleanup Complete"


# --- Final Message ---
echo "Pipeline finished successfully."
echo "Your final report is: REPORT.md"