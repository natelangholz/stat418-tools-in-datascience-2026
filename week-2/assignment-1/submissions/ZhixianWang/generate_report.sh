#!/bin/bash
# generate_report.sh - Produce REPORT.md from pre-computed analysis text files
# Reads analysis/ files instead of reprocessing raw logs (~seconds vs ~10 min)
# Usage: ./generate_report.sh [jul_analysis] [aug_analysis]

set -euo pipefail

JUL_FILE="${1:-analysis/analysis_july.txt}"
AUG_FILE="${2:-analysis/analysis_august.txt}"
REPORT="REPORT.md"

for f in "$JUL_FILE" "$AUG_FILE"; do
    [ -f "$f" ] || { echo "Error: not found: $f — run analyze_logs.sh first"; exit 1; }
done

# ── Section extractor ──────────────────────────────────────────────────────
# sec <file> <n>  →  non-blank content lines of section N
sec() {
    awk -v n="$2" '
        /^=/ { in_s=0; next }
        /^──/ {
            s=$0; gsub(/^── /,"",s); split(s,p,".")
            in_s = (p[1]+0 == n); next
        }
        in_s && /[^ \t]/ { print }
    ' "$1"
}

# ── Value extractors ───────────────────────────────────────────────────────
total_lines()  { grep "^Total log lines:" "$1" | awk '{print $NF}'; }
count_404()    { sec "$1" 5 | awk '/404 errors:/ {print $3}'; }
count_errors() { sec "$1" 12 | awk '/[0-9][0-9]:[0-9][0-9].*errors/ {s+=$2} END{print s+0}'; }
avg_bytes()    { sec "$1" 11 | awk '/Average size/ {print $4}'; }

# ── Formatters (stdin → markdown table rows) ───────────────────────────────

# "  COUNT  name"  →  "| name | COUNT |"
fmt_host() { awk '{printf "| %-45s | %8d |\n", $2, $1}'; }
fmt_url()  { awk '{printf "| %-55s | %8d |\n", $2, $1}'; }

fmt_method() { awk '{printf "| %-8s | %8d |\n", $2, $1}'; }

fmt_ip_hostname() {
    awk '
    /IP addresses/ { pct=$5; gsub(/[()]/,"",pct); printf "| IP Addresses | %s | %s |\n",$4,pct }
    /Hostnames/    { pct=$4; gsub(/[()]/,"",pct); printf "| Hostnames    | %s | %s |\n",$3,pct }
    '
}

fmt_status() {
    awk '/HTTP [0-9]/ {
        pct=$5; gsub(/[()]/,"",pct)
        printf "| %-6s | %8d | %6s |\n", $2, $4, pct
    }'
}

fmt_day() {
    awk '{ c=$2; gsub(/[()]/,"",c); printf "| %-13s | %7d |\n", $1, c+0 }'
}

fmt_hourly_rows() {
    awk '/^  [0-9][0-9]:[0-9][0-9]  / {
        bar=""; for(i=0;i<int($2/5000);i++) bar=bar"█"
        printf "| %s | %7d | %s |\n", $1, $2, bar
    }'
}

fmt_hourly_summary() {
    awk '
    /Peak hour/  { peak=$NF }
    /Quiet hour/ { quiet=$NF }
    END { printf "**Peak hour:** %s  **Quiet hour:** %s\n", peak, quiet }
    '
}

fmt_response_size() {
    awk '
    /Largest response/ { gsub(/[()]/,""); printf "| Largest | %s bytes %s |\n",$4,$6 }
    /Average size/     { printf "| Average | %s bytes |\n",$4 }
    '
}

fmt_outage() {
    awk '
    /GAP:/    { d=$3; gsub(/,/,"",d); printf "| %s | %s | gap |\n", d, $NF }
    /No gaps/ { print "| — | — | No gaps detected |" }
    '
}

# ── Error pattern sub-sections ─────────────────────────────────────────────
error_by_hour() {
    sec "$1" 12 | awk '/[0-9][0-9]:[0-9][0-9].*errors/ {printf "| %s | %s |\n",$1,$2}'
}

error_by_host() {
    sec "$1" 12 | awk '
        /Top 5 hosts/      { collect=1; next }
        /Top 5 error URLs/ { collect=0 }
        collect && /[0-9]/ { printf "| %-45s | %6d |\n", $2, $1 }
    '
}

error_by_url() {
    sec "$1" 12 | awk '
        /Top 5 error URLs/ { collect=1; next }
        collect && /[0-9]/ { printf "| %-50s | %6d |\n", $2, $1 }
    '
}

# ── Per-month sections (reused for both months) ────────────────────────────
month_report() {
    local f="$1"
    cat <<MONTH

### 1. Top 10 Hosts

| Host | Requests |
|------|----------|
$(sec "$f" 1 | fmt_host)

### 2. IP vs Hostname

| Type | Count | % |
|------|-------|---|
$(sec "$f" 2 | fmt_ip_hostname)

### 3. Top 10 Requested URLs

| URL | Requests |
|-----|----------|
$(sec "$f" 3 | fmt_url)

### 4. HTTP Methods

| Method | Count |
|--------|-------|
$(sec "$f" 4 | fmt_method)

### 5. 404 Errors

$(sec "$f" 5 | grep "404 errors:")

### 6. Response Code Distribution

| Status | Count | % |
|--------|-------|---|
$(sec "$f" 6 | fmt_status)

### 7. Hourly Activity (each █ ≈ 5 000 requests)

| Hour | Requests | Chart |
|------|----------|-------|
$(sec "$f" 7 | fmt_hourly_rows)

$(sec "$f" 7 | fmt_hourly_summary)

### 8. Busiest Day

| Date | Requests |
|------|----------|
$(sec "$f" 8 | fmt_day)

### 9. Quietest Day (≥100 requests)

| Date | Requests |
|------|----------|
$(sec "$f" 9 | fmt_day)

### 10. Data Outage Detection

| Last before gap | First after gap | Notes |
|-----------------|-----------------|-------|
$(sec "$f" 10 | fmt_outage)

### 11. Response Size

| Metric | Value |
|--------|-------|
$(sec "$f" 11 | fmt_response_size)

### 12. Error Patterns (4xx/5xx)

**Errors by hour:**

| Hour | Errors |
|------|--------|
$(error_by_hour "$f")

**Top 5 hosts generating errors:**

| Host | Errors |
|------|--------|
$(error_by_host "$f")

**Top 5 error URLs:**

| URL | Errors |
|-----|--------|
$(error_by_url "$f")
MONTH
}

# ── Build report ───────────────────────────────────────────────────────────
{
cat <<HEADER
# NASA Web Server Log Analysis Report

**Generated:** $(date)
**Analyst:** ZhixianWang

## Dataset Overview

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Total log lines | $(total_lines "$JUL_FILE") | $(total_lines "$AUG_FILE") |
| 404 errors | $(count_404 "$JUL_FILE") | $(count_404 "$AUG_FILE") |
| 4xx/5xx errors | $(count_errors "$JUL_FILE") | $(count_errors "$AUG_FILE") |
| Average response (bytes) | $(avg_bytes "$JUL_FILE") | $(avg_bytes "$AUG_FILE") |

---

## July 1995
$(month_report "$JUL_FILE")

---

## August 1995
$(month_report "$AUG_FILE")

---

## July vs August Comparison

| Metric | July | August | Change |
|--------|------|--------|--------|
| Total requests | $(total_lines "$JUL_FILE") | $(total_lines "$AUG_FILE") | $(awk -v j="$(total_lines "$JUL_FILE")" -v a="$(total_lines "$AUG_FILE")" 'BEGIN{d=a-j; printf "%+d (%.1f%%)", d, d/j*100}') |
| 404 errors | $(count_404 "$JUL_FILE") | $(count_404 "$AUG_FILE") | — |
| 4xx/5xx errors | $(count_errors "$JUL_FILE") | $(count_errors "$AUG_FILE") | — |
| Avg response bytes | $(avg_bytes "$JUL_FILE") | $(avg_bytes "$AUG_FILE") | — |

---

*Report generated by generate_report.sh — ZhixianWang*
HEADER
} > "$REPORT"

echo "Report written to $REPORT"
