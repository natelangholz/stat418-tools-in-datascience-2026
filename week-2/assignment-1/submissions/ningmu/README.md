# Homework 1 — NASA Web Server Log Analysis

**Author:** Christine (ningmu)

This submission analyses the NASA Kennedy Space Center web server access
logs from **July 1995** and **August 1995** using bash, grep, sed, awk,
and standard Unix text tools.

## Files in this directory

| File | Purpose |
|------|---------|
| `download_data.sh`   | Downloads, validates, and backs up the two raw log files. |
| `analyze_logs.sh`    | Runs the 12 required analyses on a single log file. |
| `generate_report.sh` | Runs `analyze_logs.sh` on both months and writes `REPORT.md`. |
| `run_pipeline.sh`    | Master script that chains the three above in order. |
| `REPORT.md`          | Final, auto-generated analysis report. |
| `download.log`       | Timestamped log of the download stage. |
| `pipeline.log`       | Timestamped log of the whole pipeline. |
| `data/`              | Downloaded raw log files. |
| `backup/`            | Backup copies of the original log files. |

## How to run

You need `bash`, `curl`, `awk` (gawk preferred for `mktime`), `grep`, `sed`,
and `sort`. Everything is a standard Unix environment; no extra packages
required.

### Option A: run the whole pipeline

```bash
chmod +x *.sh
./run_pipeline.sh
```

This will:

1. Download both log files (skipped if already present), validate them,
   and back them up to `backup/`.
2. Run `analyze_logs.sh` on each file, saving output to
   `analysis/jul_analysis.txt` and `analysis/aug_analysis.txt`.
3. Build the final `REPORT.md` with both months' findings, a side-by-side
   comparison table, and ASCII charts of daily volume.
4. Clean up the intermediate `analysis/` folder on exit.

### Option B: run each stage individually

```bash
./download_data.sh                          # writes data/ and backup/
./analyze_logs.sh  data/NASA_Jul95.log      # prints July analysis
./analyze_logs.sh  data/NASA_Aug95.log      # prints August analysis
./generate_report.sh                        # builds REPORT.md
```

`generate_report.sh` takes optional positional args:

```bash
./generate_report.sh <JUL_LOG> <AUG_LOG> <OUTPUT_FILE>
# defaults: data/NASA_Jul95.log, data/NASA_Aug95.log, REPORT.md
```

## What the analysis answers

For each month, `analyze_logs.sh` reports:

1. Top 10 hosts (excluding 404 errors)
2. IP addresses vs hostnames (percent)
3. Top 10 most-requested URLs (excluding 404 errors)
4. HTTP request methods with counts
5. Count and percentage of 404 errors
6. Full response-code distribution and the most frequent code
7. Activity per hour of day, plus peak/quietest 3 hours
8. Busiest day
9. Quietest day (excluding the hurricane outage, which has zero entries)
10. Outage detection — largest gap between consecutive timestamps, with
    start, end, and duration in hours/minutes/seconds
11. Max and average response size in bytes
12. Error patterns — errors per hour, top error-producing hosts, and
    top error-producing URLs

## Notes on implementation choices

- **`set -eu` without `pipefail`.** Many pipelines end in `| head -N`,
  which causes upstream `sort`/`awk` to exit with SIGPIPE (141). With
  `pipefail` that would abort the whole script. I deliberately opt out
  of `pipefail` so these legitimate early-close pipes don't fail.
- **Malformed-line filtering.** A few log lines have malformed
  timestamps or non-numeric status fields. Hour/day/outage analyses
  filter with `$4 ~ /^\[/` and the status-code distribution filters
  with `$9 ~ /^[1-5][0-9][0-9]$/` so garbage rows don't pollute output.
- **Outage detection via timestamp gap.** I convert each timestamp to
  epoch seconds with `awk`'s `mktime`, then track the maximum delta
  between consecutive rows. For August this cleanly identifies the
  Hurricane Erin outage.
- **Single-pass awk.** The largest files are ~200 MB. Where possible
  each question is a single pass over the file so the whole pipeline
  stays fast.

## Key findings (summary)

- **July 1995:** 1,891,714 requests, 10,714 × 404 (0.57%), busiest day
  Jul 13 with 134,203 requests, largest response 6.82 MB.
- **August 1995:** 1,569,898 requests, 9,978 × 404, busiest day Aug 31
  with 90,125 requests.
- **Hurricane Erin outage:** largest gap is **01/Aug/1995 14:52:01 →
  03/Aug/1995 04:36:13** — approximately **37h 44m 12s** of missing
  data. August 2 is entirely absent from the logs.
- **Most requests are for small GIFs** (NASA/KSC logos, etc.) — a
  classic pre-CDN traffic shape.
- **Peak hour is 14:00** (east-coast afternoon), quietest is 05:00.
