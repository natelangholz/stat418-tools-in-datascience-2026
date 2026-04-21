# Homework 1 – ZhixianWang

NASA web server log analysis pipeline using bash, awk, grep, and sed.

## Scripts

| Script | Purpose |
|--------|---------|
| `download_data.sh` | Download both log files, validate, and back up |
| `analyze_logs.sh` | Analyze a single log file (all 12 questions) |
| `generate_report.sh` | Produce `REPORT.md` comparing July vs August |
| `run_pipeline.sh` | Orchestrate all steps end-to-end |

## Quick Start

```bash
# From this directory:
chmod +x *.sh

# Option A — full pipeline (downloads ~180 MB)
./run_pipeline.sh

# Option B — if you already have the logs
./run_pipeline.sh --skip-download
```

After the pipeline completes you will have:
- `REPORT.md` — full findings in markdown
- `analysis/analysis_july.txt` — raw July analysis
- `analysis/analysis_august.txt` — raw August analysis
- `pipeline.log` — timestamped run log

## Running individual scripts

```bash
# Download only
./download_data.sh

# Analyze a single file
./analyze_logs.sh data/NASA_Jul95.log
./analyze_logs.sh data/NASA_Aug95.log

# Generate report (requires both logs already downloaded)
./generate_report.sh

# Test on a small sample
head -5000 data/NASA_Jul95.log > /tmp/sample.log
./analyze_logs.sh /tmp/sample.log
```

## Requirements

- bash 3.2+
- curl
- awk (gawk or mawk)
- Standard POSIX tools: grep, sed, sort, uniq, wc

## Files produced

```
submissions/ZhixianWang/
├── download_data.sh
├── analyze_logs.sh
├── generate_report.sh
├── run_pipeline.sh
├── README.md
├── REPORT.md          (generated)
├── pipeline.log       (generated)
├── data/
│   ├── NASA_Jul95.log
│   ├── NASA_Aug95.log
│   └── backup/
└── analysis/
    ├── analysis_july.txt
    └── analysis_august.txt
```
