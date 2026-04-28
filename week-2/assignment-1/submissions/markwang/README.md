This project analyzes the July and August 1995 NASA web server logs using a small Bash pipeline.

## Files

- `download_data.sh`: downloads `NASA_Jul95.log` and `NASA_Aug95.log`
- `analyze_logs.sh`: runs analysis on one log file and prints the results to the terminal
- `generate_report.sh`: generates a markdown report comparing the July and August logs
- `run_pipeline.sh`: runs the full workflow from download through report generation

## Requirements

- Bash
- Standard Unix tools such as `awk`, `sort`, `grep`, `sed`, `wc`, and `curl`
- Internet access to download the log files

## How to run the scripts

Make the scripts executable if needed:

```bash
chmod +x download_data.sh analyze_logs.sh generate_report.sh run_pipeline.sh
```

### 1. Download the data

```bash
./download_data.sh
```

This downloads:

- `NASA_Jul95.log`
- `NASA_Aug95.log`

It also writes download details to `download.log`.

### 2. Analyze a single log file

For the July log:

```bash
./analyze_logs.sh NASA_Jul95.log
```

For the August log:

```bash
./analyze_logs.sh NASA_Aug95.log
```

If you want to save the output to a text file:

```bash
./analyze_logs.sh NASA_Jul95.log > july_analysis.txt
./analyze_logs.sh NASA_Aug95.log > august_analysis.txt
```

### 3. Generate the report

```bash
./generate_report.sh
```

By default, this uses `NASA_Jul95.log` and `NASA_Aug95.log` and creates:

- `NASA_WebServer_Analysis_Report.md`

You can also pass log file names manually:

```bash
./generate_report.sh NASA_Jul95.log NASA_Aug95.log
```

### 4. Run the full pipeline

```bash
./run_pipeline.sh
```

This script:

1. Downloads the two NASA log files
2. Runs analysis on both logs
3. Generates the final markdown report
4. Writes a pipeline log file named something like `pipeline_run_YYYYMMDD_HHMMSS.log`

## Expected output

After running the full pipeline, the main output files should be:

- `NASA_Jul95.log`
- `NASA_Aug95.log`
- `download.log`
- `NASA_WebServer_Analysis_Report.md`
- `pipeline_run_*.log`

## Notes

- `download_data.sh` creates backup copies if the log files already exist.
- `run_pipeline.sh` may remove cached analysis text files at the end unless the keep-cache option is used.
