# Homework 1 - NASA Web Server Log Analysis

## How to Run

### Run everything at once (recommended):
```bash
bash run_pipeline.sh
```

### Or run each step individually:
```bash
bash download_data.sh          # Step 1: Download logs
bash analyze_logs.sh NASA_Jul95.log > july_results.txt  # Step 2: Analyze July
bash analyze_logs.sh NASA_Aug95.log > aug_results.txt   # Step 3: Analyze August
bash generate_report.sh        # Step 4: Generate report
```

## Files
- `download_data.sh` — Downloads and validates NASA log files
- `analyze_logs.sh` — Analyzes a log file across 12 metrics
- `generate_report.sh` — Compiles results into REPORT.md
- `run_pipeline.sh` — Runs all steps in order
- `REPORT.md` — Final analysis findings

## Notes
- Analysis takes ~30 minutes per log file due to file size (~1.9M lines)
- Tested on Ubuntu 24 via WSL2 on Windows 11
