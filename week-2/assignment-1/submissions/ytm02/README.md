# Assignment 1 — NASA Web Server Log Analysis

**Student:** ytm02
**Course:** STAT 418 (Tools in Data Science)
**Week:** 2

This folder contains my solution to Assignment 1. It analyses the NASA
Kennedy Space Center web-server access logs from **July 1995** and
**August 1995** using bash, awk, sed, grep, sort, uniq and friends.

## Files

| File | Purpose |
|---|---|
| `download_data.sh` | Part 1 — downloads both log files, validates, backs up, logs every operation |
| `analyze_logs.sh`  | Part 2 — answers all twelve analysis questions for a single log file |
| `generate_report.sh` | Part 3 — assembles the per-month outputs into `REPORT.md` |
| `run_pipeline.sh` | Part 4 — master driver that runs everything end-to-end |
| `REPORT.md` | The final markdown report (produced by `generate_report.sh`) |
| `work/` | Working directory (auto-created). Holds `data/`, `jul/`, `aug/` and run logs |

## Quick start

```bash
# Make the scripts executable (one-time)
chmod +x *.sh

# Run the whole pipeline
./run_pipeline.sh
```

That will:

1. Download `NASA_Jul95.log` and `NASA_Aug95.log` into `work/data/`
2. Validate the downloads (file size, line count, format sanity check)
3. Create gzip-compressed backups in `work/data/backup/`
4. Analyze each month separately, producing per-question output files in
   `work/jul/` and `work/aug/`
5. Assemble `REPORT.md` combining both months, with a comparison section
6. Clean up the large intermediate `normalized.tsv` files

## Running each step individually

```bash
# 1) Download
./download_data.sh work/data

# 2) Analyze each month (produces one folder of per-question text files)
./analyze_logs.sh work/data/NASA_Jul95.log work/jul
./analyze_logs.sh work/data/NASA_Aug95.log work/aug

# 3) Generate the report
./generate_report.sh work/jul work/aug REPORT.md
```

## Testing on a small sample

While iterating I found it useful to test on a few thousand lines before
running the full pipeline on the ~180MB August log:

```bash
head -10000 work/data/NASA_Jul95.log > /tmp/sample.log
./analyze_logs.sh /tmp/sample.log /tmp/sample_out
```

## Design notes

### Parsing strategy

A single pass through each raw log file produces a tab-separated
intermediate file (`normalized.tsv`) with the columns:

```
host \t date \t hour \t method \t url \t status \t bytes
```

Every subsequent question is answered by a short awk/sort/uniq pipeline
over this intermediate, which is much faster than re-parsing the raw
log twelve times.

Parsing uses `match()` with regex on the raw line to extract the
bracketed timestamp and the quoted request, rather than positional
whitespace splitting. That's more robust because URLs occasionally
contain spaces which would break `$7` indexing.

### Outage detection (Q10)

Every timestamp is converted to epoch seconds with `mktime`, sorted,
and the gap between each consecutive pair of entries is computed. The
single largest gap identifies when data collection stopped and when it
resumed, along with the total duration. For August 1995 this correctly
surfaces the Hurricane Erin outage (~37.7 hours).

### Error handling

- `set -euo pipefail` in every script
- `download_data.sh` validates file size, line count, and format
  sanity (a Common Log Format line must appear in the first 20 lines)
  before declaring success
- `run_pipeline.sh` has an `ERR` trap that prints the failing line
- All operations are logged with ISO-8601 UTC timestamps

### What I used AI assistants for

Consistent with the assignment guidance, I used AI assistants for:
syntax reminders on awk's `match()` / `mktime()`, explaining why
`$NF-1` wasn't right when the request has spaces, and code review on
the regex that extracts the bracketed timestamp. I designed the
pipeline architecture (single normalized intermediate, one output
file per question) and wrote the analysis logic myself.

## Requirements

- `bash` 4+
- `awk` (gawk or BWK awk — both support `mktime()` / `strftime()`)
- `curl`
- `gzip`, `sort`, `uniq`, `grep`, `sed`, `wc`

Tested on macOS with Homebrew `gawk` installed, and on Ubuntu 22.04.
