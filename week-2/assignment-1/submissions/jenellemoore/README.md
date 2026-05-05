# Assignment 1: Web Server Log Analysis with Bash

## Overview

This assignment analyzes NASA web server logs from July and August 1995 using Bash scripting and command line tools.

The pipeline includes:
- downloading the raw log files
- analyzing the logs
- generating a markdown report
- running the full workflow through one master pipeline script

## Data Source

NASA web server logs from July and August 1995:
- **July**: https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log
- **August**: https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log

**Log Format:**
```
host logname time method request protocol status bytes
```
## Files Included

- `download_data.sh`  
  Downloads the NASA July and August 1995 web server log files and creates backups.

- `analyze_logs.sh`  
  Performs data analysis on the July and August log datasets.

- `generate_report.sh`  
  Generates `REPORT.md`, a markdown report containing analysis results, comparisons, and summary findings.

- `run_pipeline.sh`  
  Master pipeline script that runs the full workflow in order:
  1. downloads/checks data
  2. runs analysis
  3. generates report
  4. cleans temporary files

- `REPORT.md`  
  Final report with results and findings.


## Requirements
This assignment uses:

- Bash shell
- awk
- grep
- sort
- uniq
- wc
- head
- tail
- curl

## How to Run

```bash
chmod +x download_data.sh analyze_logs.sh generate_report.sh run_pipeline.sh
./run_pipeline.sh
cat REPORT.md
```

## Output
Running the pipeline generates:

- NASA_Jul95.log
- NASA_Aug95.log
- REPORT.md

## Extra
- Temporary files are removed automatically by `run_pipeline.sh`
- Raw log files are preserved
- REPORT.md contains all final findings