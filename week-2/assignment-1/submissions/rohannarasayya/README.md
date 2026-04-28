# NASA Web Server Log Analysis

Bash pipeline to download, analyze, and report on NASA Kennedy Space Center
web server access logs from July and August 1995.

## Quick start

Run the full pipeline (download → analyze → report) with one command:

```bash
bash run_pipeline.sh
```

The final report is written to `REPORT.md`.

## Scripts

### `download_data.sh`

Downloads both log files, validates their size and line counts, and creates
backups.

```bash
bash download_data.sh
```

**Outputs:**
- `NASA_Jul95.log` (~197 MB, ~1.9M lines)
- `NASA_Aug95.log` (~160 MB, ~1.6M lines)
- `NASA_Jul95.log.bak` / `NASA_Aug95.log.bak`

Requires `curl`. Logs every operation with timestamps to stdout.

---

### `analyze_logs.sh`

Analyzes a single log file and prints answers to 12 questions covering
traffic patterns, response codes, error rates, and the August hurricane
outage.

```bash
bash analyze_logs.sh <logfile>
```

**Example:**

```bash
bash analyze_logs.sh NASA_Jul95.log
bash analyze_logs.sh NASA_Aug95.log

# Test on a small sample first
head -1000 NASA_Jul95.log > test_sample.log
bash analyze_logs.sh test_sample.log
```

**Questions answered:**

| # | Question |
|---|----------|
| 1 | Top 10 hosts (excluding 404s) |
| 2 | % requests from IP addresses vs hostnames |
| 3 | Top 10 URLs (excluding 404s) |
| 4 | HTTP method counts |
| 5 | Total 404 error count |
| 6 | Most frequent response code and its percentage |
| 7 | Request count by hour of day |
| 8 | Busiest date |
| 9 | Quietest date (excluding outage dates) |
| 10 | Hurricane outage detection (missing days in date range) |
| 11 | Largest and average response size in bytes |
| 12 | Error patterns by hour and host |

---

### `generate_report.sh`

Runs `analyze_logs.sh` on both log files and writes a comprehensive
`REPORT.md` containing the full analysis output, a side-by-side July vs
August comparison table, ASCII bar charts of hourly traffic, and a key
findings section highlighting the hurricane outage.

```bash
bash generate_report.sh
```

Requires `NASA_Jul95.log` and `NASA_Aug95.log` to be present in the same
directory (run `download_data.sh` first).

**Output:** `REPORT.md`

---

### `run_pipeline.sh`

Master script that runs all four stages in order with progress updates,
per-step timing, error checking, and cleanup of temporary files.

```bash
bash run_pipeline.sh
```

**Stages:**

```
[Step 1/4] Downloading and validating log files...
[Step 2/4] Analyzing July logs...
[Step 3/4] Analyzing August logs...
[Step 4/4] Generating report...
[Cleanup]  Removing temporary files...
```

If any step fails its exit code check, the pipeline prints `[ERROR] <reason>`
and stops immediately. On success it prints:

```
Pipeline complete! See REPORT.md for results.
```

## Requirements

- bash 4+
- `awk` (gawk or mawk; uses `mktime`/`strftime` in Q10)
- `curl` (for `download_data.sh`)
- Standard POSIX utilities: `sort`, `uniq`, `wc`, `grep`, `sed`

## Data source

NASA Kennedy Space Center HTTP access logs, July and August 1995.
Original files hosted at `https://atlas.cs.brown.edu/data/web-logs/`.
