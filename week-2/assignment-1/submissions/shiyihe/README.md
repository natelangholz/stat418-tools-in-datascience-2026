# NASA Web Server Log Analysis with Bash

## Files

- `download_data.sh`
  Downloads the July and August 1995 NASA log files, validates them, creates backups, and writes a log file.

- `analyze_logs.sh`
  Analyzes the log files and saves summary results in the `results` folder.

- `generate_report.sh`
  Generates `REPORT.md` from the analysis results.

- `run_pipeline.sh`
  Runs the full pipeline from start to finish.

## How to run

Run the full pipeline:

bash run_pipeline.sh

Or run each step separately:

bash download_data.sh
bash analyze_logs.sh
bash generate_report.sh

## Output

- Analysis summaries:
  - `results/NASA_Jul95_summary.txt`
  - `results/NASA_Aug95_summary.txt`

- Final report:
  - `REPORT.md`

## Notes

- The scripts use bash, awk, grep, sort, uniq, and other command line tools.
- ASCII charts are included in `REPORT.md`.
- Temporary test files are removed by `run_pipeline.sh`.
