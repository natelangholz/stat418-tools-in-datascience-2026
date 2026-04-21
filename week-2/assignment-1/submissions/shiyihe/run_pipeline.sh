#!/bin/bash

set -e

echo "Starting pipeline..."
echo ""

if [ ! -f download_data.sh ]; then
    echo "download_data.sh not found"
    exit 1
fi

if [ ! -f analyze_logs.sh ]; then
    echo "analyze_logs.sh not found"
    exit 1
fi

if [ ! -f generate_report.sh ]; then
    echo "generate_report.sh not found"
    exit 1
fi

echo "Step 1: Downloading and validating data..."
bash download_data.sh
echo "Step 1 finished."
echo ""

echo "Step 2: Analyzing logs..."
bash analyze_logs.sh
echo "Step 2 finished."
echo ""

echo "Step 3: Generating report..."
bash generate_report.sh
echo "Step 3 finished."
echo ""

echo "Step 4: Cleaning temporary files..."
rm -f data/test_Jul95.log data/test_Aug95.log
echo "Step 4 finished."
echo ""

echo "Pipeline completed successfully."
echo "Final report: REPORT.md"

