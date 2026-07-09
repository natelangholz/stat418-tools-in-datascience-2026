# Assignment 1 Submission

This assignment analyzes the NASA web server logs from July 1995 and August 1995 using bash scripts. The pipeline downloads the data, performs the required analysis, and generates a final markdown report.

## Files Included

- `download_data.sh`  
  Downloads both log files, validates the downloads, creates backup copies, and logs all operations with timestamps.

- `analyze_logs.sh`  
  Performs the required analysis for each log file, including basic analysis, time-based analysis, and advanced analysis.

- `generate_report.sh`  
  Generates a markdown report with summary statistics, comparisons between July and August, visualizations, and full analysis outputs.

- `run_pipeline.sh`  
  Runs the full workflow in the correct order and handles errors at each stage.

- `REPORT.md`  
  Final report containing the main findings, comparisons, charts, and appendices with the full analysis results.

## How to Run

First, make the scripts executable:

```bash
chmod +x download_data.sh analyze_logs.sh generate_report.sh run_pipeline.sh