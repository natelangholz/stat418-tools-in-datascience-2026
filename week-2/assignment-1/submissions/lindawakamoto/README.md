## How to Run

## Paste this line in the terminal to run the pipeline:
bash run_pipeline.sh

## Pipeline Structure:
- download_data.sh: fetches data and validates logs
- analyze_logs.sh: computes metrics for various analysis questions
- generate_report.sh: creates a report with visualizations as REPORT.md
- run_pipeline.sh: orchestrates everything

# For any troubleshooting, run these before running the pipeline:
## for Mac, run this to use simplest possible standard for all programs
export LC_ALL=C
## run this to remove weird characters
sed -i '' 's/\r$//' *.sh
## run this to make sure files are executable
chmod +x *.sh 