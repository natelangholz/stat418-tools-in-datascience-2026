# Homework 1 Submission

## Files
- `download_data.sh`
- `analyze_logs.sh`
- `generate_report.sh`
- `run_pipeline.sh`
- `REPORT.md`

## How to run

```bash
chmod +x download_data.sh analyze_logs.sh generate_report.sh run_pipeline.sh
./run_pipeline.sh
```

This will:

1. Download the July and August NASA logs
2. Validate the downloads and create backups
3. Analyze both files
4. Generate `REPORT.md`

## Notes
- The scripts use streaming command-line tools rather than loading the full logs into memory.
- The outage is identified by the largest timestamp gap in the August file.
- The scripts follow the course emphasis on modular pipelines, reproducibility, error handling, and bash-based data analysis.
