#!/bin/bash
# run_pipeline.sh - Run the full NASA log analysis pipeline

# Helper to print a step header
progress() {
  echo ""
  echo "========================================"
  echo "  $1"
  echo "========================================"
  echo ""
}

# Helper to check if the last command succeeded
check_error() {
  if [ $? -ne 0 ]; then
    echo "ERROR: $1 failed. Stopping pipeline."
    exit 1
  fi
}

# Create the output directory if it doesn't exist
mkdir -p output
mkdir -p logs

progress "Step 1 of 4: Downloading log files"
bash download_data.sh 2>&1 | tee logs/download.log
check_error "download_data.sh"
echo "Download complete. Log saved to logs/download.log"

progress "Step 2 of 4: Analyzing log files"
bash analyze_logs.sh NASA_Jul95.log NASA_Aug95.log
check_error "analyze_logs.sh"
echo "Analysis complete."

progress "Step 3 of 4: Generating report"
bash generate_report.sh NASA_Jul95.log NASA_Aug95.log
check_error "generate_report.sh"
echo "Report complete. Saved to REPORT.md"

progress "Step 4 of 4: Cleaning up temporary files"
# Remove any .tmp files that may have been created during processing
rm -f *.tmp
echo "Cleanup complete."

progress "Pipeline finished!"
