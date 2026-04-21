#!/bin/bash
# analyze_logs.sh - Analyze a single NASA web server log file
# Usage: ./analyze_logs.sh <logfile>
#
# Log format:
#   host - - [DD/Mon/YYYY:HH:MM:SS -TZ] "METHOD /path HTTP/x.x" STATUS BYTES
# AWK fields (split on whitespace):
#   $1=host  $4=[datetime  $6="METHOD  $7=URL  $9=status  $10=bytes

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <logfile>"
    exit 1
fi

LOG="$1"

if [ ! -f "$LOG" ]; then
    echo "Error: file not found: $LOG"
    exit 1
fi

LABEL=$(basename "$LOG" .log)

# ── Helpers ────────────────────────────────────────────────────────────────
section() { echo; echo "── $* ──"; }

# ── Summary ────────────────────────────────────────────────────────────────
echo "========================================"
echo "  Analysis: $LABEL"
echo "  $(date)"
echo "========================================"

TOTAL=$(wc -l < "$LOG")
echo "Total log lines: $TOTAL"

# ── 1. Top 10 hosts (exclude 404s) ─────────────────────────────────────────
section "1. Top 10 Hosts (excluding 404 responses)"
awk '$9 != 404 {count[$1]++} END {for (h in count) print count[h], h}' "$LOG" \
    | sort -rn | awk 'NR<=10 {printf "  %8d  %s\n", $1, $2}'

# ── 2. IP vs Hostname ──────────────────────────────────────────────────────
section "2. IP Addresses vs Hostnames"
awk '
{
    total++
    if ($1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) ip++
    else hostname++
}
END {
    printf "  IP addresses : %d (%.1f%%)\n", ip,      ip/total*100
    printf "  Hostnames    : %d (%.1f%%)\n", hostname, hostname/total*100
    printf "  Total        : %d\n", total
}' "$LOG"

# ── 3. Top 10 requested URLs (exclude 404s) ────────────────────────────────
section "3. Top 10 Requested URLs (excluding 404 responses)"
awk '$9 != 404 {count[$7]++} END {for (u in count) print count[u], u}' "$LOG" \
    | sort -rn | awk 'NR<=10 {printf "  %8d  %s\n", $1, $2}'

# ── 4. HTTP methods ────────────────────────────────────────────────────────
section "4. HTTP Methods"
awk '{
    method = substr($6, 2)
    gsub(/"/, "", method)
    if (method ~ /^[A-Z]+$/) count[method]++
}
END {for (m in count) print count[m], m}' "$LOG" \
    | sort -rn \
    | awk '{printf "  %8d  %s\n", $1, $2}'

# ── 5. 404 error count ────────────────────────────────────────────────────
section "5. 404 Errors"
COUNT_404=$(awk '$9 == 404' "$LOG" | wc -l)
PCT_404=$(awk -v c="$COUNT_404" -v t="$TOTAL" 'BEGIN {printf "%.2f", c/t*100}')
echo "  404 errors: $COUNT_404 ($PCT_404% of all requests)"

# ── 6. Response code distribution ─────────────────────────────────────────
section "6. Response Code Distribution"
awk '$9 ~ /^[0-9]+$/ {count[$9]++}
END {for (c in count) print count[c], c}' "$LOG" \
    | sort -rn \
    | awk -v t="$TOTAL" 'NR<=10 {printf "  HTTP %-4s : %8d  (%.1f%%)\n", $2, $1, $1/t*100}'

# ── 7. Peak hours ─────────────────────────────────────────────────────────
section "7. Requests by Hour of Day"
awk '{
    hour = substr($4, 14, 2)
    if (hour ~ /^[0-9][0-9]$/) count[hour]++
}
END {for (h in count) print h, count[h]}' "$LOG" \
    | sort -k1 \
    | awk '
BEGIN { max=0 }
{ if ($2 > max) { max=$2; peak_h=$1 } if ($2 < min || NR==1) { min=$2; quiet_h=$1 } }
{ printf "  %s:00  %d\n", $1, $2 }
END { print ""; printf "  Peak hour  : %s:00\n", peak_h; printf "  Quiet hour : %s:00\n", quiet_h }'

# ── 8. Busiest day ────────────────────────────────────────────────────────
section "8. Busiest Day"
awk '{
    # $4 = [DD/Mon/YYYY:HH:MM:SS
    date = substr($4, 2, 11)   # DD/Mon/YYYY
    count[date]++
}
END {for (d in count) print count[d], d}' "$LOG" \
    | sort -rn | awk 'NR==1 {printf "  %s  (%d requests)\n", $2, $1}'

# ── 9. Quietest day (excluding outage days with near-zero traffic) ─────────
section "9. Quietest Day (excluding days with < 100 requests)"
awk '{
    date = substr($4, 2, 11)
    count[date]++
}
END {for (d in count) print count[d], d}' "$LOG" \
    | awk '$1 >= 100' \
    | sort -n | awk 'NR==1 {printf "  %s  (%d requests)\n", $2, $1}'

# ── 10. Hurricane outage detection ────────────────────────────────────────
section "10. Data Outage Detection (missing date gaps)"
awk '{
    date = substr($4, 2, 11)
    if (date ~ /^[0-9]/) seen[date] = 1
}
END {for (d in seen) print d}' "$LOG" \
    | sort \
    | awk '
BEGIN {
    split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec", m)
    for (i=1; i<=12; i++) month_num[m[i]] = i
    dm[1]=31; dm[2]=28; dm[3]=31; dm[4]=30; dm[5]=31; dm[6]=30
    dm[7]=31; dm[8]=31; dm[9]=30; dm[10]=31; dm[11]=30; dm[12]=31
    gaps = 0
}
{
    split($1, p, "/")
    day = p[1]+0; mon = month_num[p[2]]; year = p[3]+0

    if (NR > 1) {
        en = prev_day + 1; em = prev_mon
        if (en > dm[prev_mon]) { en = 1; em = prev_mon + 1 }
        if (day != en || mon != em) {
            printf "  GAP: after %s, next recorded date is %s\n", prev_label, $1
            gaps++
        }
    }
    prev_day = day; prev_mon = mon; prev_label = $1
}
END { if (gaps == 0) print "  No gaps detected." }'

# ── 11. Response size statistics ──────────────────────────────────────────
section "11. Response Size (bytes)"
awk '
$10 ~ /^[0-9]+$/ {
    bytes = $10 + 0
    total += bytes
    count++
    if (bytes > max) { max = bytes; max_url = $7 }
}
END {
    printf "  Largest response : %d bytes  (%s)\n", max, max_url
    printf "  Average size     : %.0f bytes\n", (count > 0 ? total/count : 0)
    printf "  Requests with bytes reported: %d\n", count
}' "$LOG"

# ── 12. Error patterns ────────────────────────────────────────────────────
section "12. Error Patterns (4xx/5xx)"

echo "  Errors by hour:"
awk '$9~/^[0-9]+$/ && $9 >= 400 {
    hour = substr($4, 14, 2)
    if (hour ~ /^[0-9][0-9]$/) count[hour]++
}
END {for (h in count) print h, count[h]}' "$LOG" \
    | sort -k1 \
    | awk '{printf "    %s:00  %d errors\n", $1, $2}'

echo
echo "  Top 5 hosts generating errors:"
awk '$9~/^[0-9]+$/ && $9 >= 400 {count[$1]++} END {for (h in count) print count[h], h}' "$LOG" \
    | sort -rn | awk 'NR<=5 {printf "    %8d  %s\n", $1, $2}'

echo
echo "  Top 5 error URLs:"
awk '$9~/^[0-9]+$/ && $9 >= 400 {count[$7]++} END {for (u in count) print count[u], u}' "$LOG" \
    | sort -rn | awk 'NR<=5 {printf "    %8d  %s\n", $1, $2}'

echo
echo "========================================"
echo "  Done: $LABEL"
echo "========================================"
