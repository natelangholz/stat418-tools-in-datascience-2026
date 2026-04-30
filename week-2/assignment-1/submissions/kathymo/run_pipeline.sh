# permission: chmod +x run_pipeline.sh
# to run: bash run_pipeline.sh

#!/bin/bash
set -euo pipefail

# Text Formatting for Updates
BOLD=$(tput bold)
GREEN=$(tput setaf 2)
YELLOW=$(tput setaf 3)
RED=$(tput setaf 1)
RESET=$(tput sgr0)

# Configuration
SCRIPTS=("download_data.sh" "analyze_logs.sh" "generate_report.sh")
TEMP_DATA="analysis_results.txt"
FINAL_REPORT="REPORT.md"

echo "${BOLD}Starting NASA Analysis Pipeline...${RESET}"
echo "----------------------------------------------------"

# Function to verify scripts exist and are executable
check_dependencies() {
    for script in "${SCRIPTS[@]}"; do
        if [[ ! -f "$script" ]]; then
            echo "${RED}ERROR: $script is missing!${RESET}" >&2
            exit 1
        fi
        chmod +x "$script"
    done
}

# 1. Dependency Check
check_dependencies

# 2. Stage 1: Download Data
echo "${YELLOW}[1/4]${RESET} Downloading NASA log files..."
if ./download_data.sh; then
    echo "${GREEN}  - Download and validation successful.${RESET}"
else
    echo "${RED}  - Download failed. Check setup.log for details.${RESET}" >&2
    exit 1
fi

# 3. Stage 2: Log Analysis
echo "${YELLOW}[2/4]${RESET} Running deep-dive analysis on logs..."
# This script internally populates analysis_results.txt
if ./analyze_logs.sh; then
    echo "${GREEN}  - Analysis complete. Temporary data stored.${RESET}"
else
    echo "${RED}  - Analysis stage failed.${RESET}" >&2
    exit 1
fi

# 4. Stage 3: Generate Markdown Report
echo "${YELLOW}[3/4]${RESET} Building final Markdown report..."
if ./generate_report.sh; then
    echo "${GREEN}  - Report built successfully: $FINAL_REPORT${RESET}"
else
    echo "${RED}  - Report generation failed.${RESET}" >&2
    exit 1
fi

# 5. Stage 4: Cleanup
echo "${YELLOW}[4/4]${RESET} Performing cleanup..."
if rm "$TEMP_DATA"; then
    echo "${GREEN}  - Temporary file $TEMP_DATA removed.${RESET}"
else
    echo "${YELLOW}  - Warning: Could not remove $TEMP_DATA${RESET}"
fi

# Final Summary
echo "----------------------------------------------------"
echo "${BOLD}${GREEN}PIPELINE COMPLETE!${RESET}"
echo "You can view your results in: ${BOLD}$FINAL_REPORT${RESET}"
echo "----------------------------------------------------"