# Assignment 1: Web Server Log Analysis with Bash
# Amber Jiang - Stats 418

Analysis of NASA web server access logs from July and August 1995.

## How to Run 

### Run full pipeline

This downloads the data, runs the analysis, and generates the report in one step:

```bash
bash run_pipeline.sh
```

### Run scripts individually

**1. Download the log files:**
```bash
bash download_data.sh
```

**2. Analyze the logs:**
```bash
bash analyze_logs.sh NASA_Jul95.log NASA_Aug95.log
```

**3. Generate the markdown report:**
```bash
bash generate_report.sh
```

## Requirements

- `bash`
- Standard Unix tools: `awk`, `grep`, `sed`, `sort`, `curl`
