#!/bin/bash

set -eu

echo "=== Starting NASA Log Analysis Pipeline ==="

# check for any error during download
echo "[1/4] Downloading data..."
./download_data.sh || { echo "Download failed"; exit 1; }

# check log files for expected line counts (should be > 0)
echo "[2/4] Validating data..."
JULY="NASA_Jul95.log"
AUG="NASA_Aug95.log"

[ -s "$JULY" ] || { echo "ERROR: July file missing/empty"; exit 1; }
[ -s "$AUG" ] || { echo "ERROR: August file missing/empty"; exit 1; }

# check for any error during analysis script
echo "[3/4] Running analysis..."
./analyze_logs.sh || { echo "Analysis failed"; exit 1; }

# check for any error during report generation and that report file is created
echo "[4/4] Generating report..."
./generate_report.sh || { echo "Report generation failed"; exit 1; }
[ -e report.md ] || { echo "Report file not created"; exit 1; }

# remove temporary files if they exist
echo "Cleaning up..."
rm -f ./*.tmp

echo "=== Pipeline completed successfully ==="