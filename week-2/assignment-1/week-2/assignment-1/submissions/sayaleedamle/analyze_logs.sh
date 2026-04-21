#!/bin/bash
# analyze_logs.sh - Basic analysis of NASA web server logs
# Usage: ./analyze_logs.sh <logfile>

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Usage: $0 <logfile>" >&2
    exit 1
fi

LOG="$1"

if [ ! -f "$LOG" ]; then
    echo "ERROR: File not found: $LOG" >&2
    exit 1
fi

echo "======================================================"
echo "Analysis: $LOG"
echo "======================================================"

# Fields: $1=host, $(NF-1)=status, $NF=bytes
# Using NF-relative positions handles lines missing the HTTP/version token.

# 1. Top 10 hosts (exclude 404 errors)
echo ""
echo "--- Top 10 Hosts (excluding 404 errors) ---"
awk '$(NF-1) != 404 {print $1}' "$LOG" | sort | uniq -c | sort -rn | head -10 | \
    awk '{printf "%8d  %s\n", $1, $2}'

# 2. IP vs Hostname percentage
echo ""
echo "--- IP Address vs Hostname ---"
awk '{
    if ($1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) ip++
    else host++
    total++
}
END {
    printf "IP addresses: %d (%.1f%%)\n", ip, ip/total*100
    printf "Hostnames:    %d (%.1f%%)\n", host, host/total*100
    printf "Total:        %d\n", total
}' "$LOG"

# 3. Top 10 requested URLs (exclude 404 errors)
echo ""
echo "--- Top 10 Requested URLs (excluding 404 errors) ---"
awk '$(NF-1) != 404 {print $7}' "$LOG" | sort | uniq -c | sort -rn | head -10 | \
    awk '{printf "%8d  %s\n", $1, $2}'

# 4. Request types (HTTP methods)
echo ""
echo "--- HTTP Request Methods ---"
awk '{gsub(/"/, "", $6); print $6}' "$LOG" | sort | uniq -c | sort -rn | \
    awk '{printf "%8d  %s\n", $1, $2}'

# 5. 404 error count
echo ""
echo "--- 404 Errors ---"
awk '$(NF-1) == 404 {count++} END {printf "Total 404 errors: %d\n", count}' "$LOG"

# 6. Most frequent response code and its percentage
echo ""
echo "--- Response Code Breakdown ---"
awk '{codes[$(NF-1)]++; total++}
END {
    for (c in codes) if (codes[c] > max) { max = codes[c]; top = c }
    printf "Most frequent: %s (%d requests, %.1f%%)\n\n", top, max, max/total*100
    for (c in codes) print codes[c], c
}' "$LOG" | awk 'NR==1{print; next} NF==2{printf "%8d  %s\n", $1, $2}' | \
    awk 'NR==1{print; next} {print | "sort -rn"}'

# ---- Time-Based Analysis ----

# 7. Peak hours
# $4 looks like [01/Jul/1995:00:00:01 — split on ":" gives [date, HH, MM, SS -0400]
echo ""
echo "--- Peak Hours (requests by hour of day) ---"
awk '{
    n = split($4, a, ":")
    if (n >= 2) hours[a[2]]++
}
END {
    for (h in hours) printf "%s %d\n", h, hours[h]
}' "$LOG" | sort -n | awk '{printf "Hour %s: %d requests\n", $1, $2}'

echo ""
echo "Top 3 busiest hours:"
awk '{
    n = split($4, a, ":")
    if (n >= 2) hours[a[2]]++
}
END {
    for (h in hours) printf "%d %s\n", hours[h], h
}' "$LOG" | sort -rn | head -3 | awk '{printf "  Hour %s: %d requests\n", $2, $1}'

echo "Top 3 quietest hours:"
awk '{
    n = split($4, a, ":")
    if (n >= 2) hours[a[2]]++
}
END {
    for (h in hours) printf "%d %s\n", hours[h], h
}' "$LOG" | sort -n | head -3 | awk '{printf "  Hour %s: %d requests\n", $2, $1}'

# 8. Busiest day
# substr($4, 2, 11) strips the leading "[" to get "01/Jul/1995"
echo ""
echo "--- Busiest Day ---"
awk '{
    day = substr($4, 2, 11)
    if (length(day) == 11) days[day]++
}
END {
    for (d in days) printf "%d %s\n", days[d], d
}' "$LOG" | sort -rn | head -1 | awk '{printf "Busiest day: %s (%d requests)\n", $2, $1}'

# 9. Quietest day (exclude outage dates — days with fewer than 100 requests)
echo ""
echo "--- Quietest Day (excluding outage dates with < 100 requests) ---"
awk '{
    day = substr($4, 2, 11)
    if (length(day) == 11) days[day]++
}
END {
    for (d in days) if (days[d] >= 100) printf "%d %s\n", days[d], d
}' "$LOG" | sort -n | head -1 | awk '{printf "Quietest day: %s (%d requests)\n", $2, $1}'

# ---- Advanced Analysis ----

# 10. Hurricane outage (August only)
# Find gaps > 1 hour between consecutive log entries by comparing sorted timestamps.
echo ""
echo "--- Hurricane / Data Outage Detection ---"
awk '{print $4}' "$LOG" | sed 's/\[//' | sort | awk '
BEGIN {
    split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec", months_arr)
    for (i=1; i<=12; i++) month_num[months_arr[i]] = i
}
function ts(stamp,   parts, dp, tp, y, mo, d, h, mi, s) {
    # stamp format: 01/Aug/1995:00:00:01
    split(stamp, parts, /[\/:]/)
    d  = parts[1]+0; mo = month_num[parts[2]]; y = parts[3]+0
    h  = parts[4]+0; mi = parts[5]+0;           s = parts[6]+0
    return mktime(y " " mo " " d " " h " " mi " " s)
}
NR==1 { prev = $1; next }
{
    cur_ts  = ts($1)
    prev_ts = ts(prev)
    gap = cur_ts - prev_ts
    if (gap > 3600) {
        gap_h = int(gap/3600)
        gap_m = int((gap % 3600)/60)
        printf "Gap: %s  -->  %s  (%dh %dm)\n", prev, $1, gap_h, gap_m
    }
    prev = $1
}' 2>/dev/null || echo "(mktime not supported — run on GNU awk/gawk for outage detection)"

# 11. Response size (largest and average)
echo ""
echo "--- Response Size ---"
awk '
$NF ~ /^[0-9]+$/ {
    bytes = $NF + 0
    if (bytes > max) { max = bytes; max_url = $7 }
    total += bytes; count++
}
END {
    printf "Largest response: %d bytes  (%s)\n", max, max_url
    printf "Average response: %.0f bytes\n", (count > 0 ? total/count : 0)
    printf "Total requests with byte data: %d\n", count
}' "$LOG"

# 12. Error patterns
echo ""
echo "--- Error Patterns ---"
echo "Errors (4xx/5xx) by hour:"
awk '$(NF-1) ~ /^[45]/ {
    n = split($4, a, ":")
    if (n >= 2) errhours[a[2]]++
}
END {
    for (h in errhours) printf "%s %d\n", h, errhours[h]
}' "$LOG" | sort -n | awk '{printf "  Hour %s: %d errors\n", $1, $2}'

echo ""
echo "Top 5 hosts generating errors (4xx/5xx):"
awk '$(NF-1) ~ /^[45]/ {print $1}' "$LOG" | sort | uniq -c | sort -rn | head -5 | \
    awk '{printf "  %8d  %s\n", $1, $2}'

echo ""
echo "Error breakdown by response code:"
awk '$(NF-1) ~ /^[45]/ {codes[$(NF-1)]++}
END { for (c in codes) printf "%d %s\n", codes[c], c }' "$LOG" | \
    sort -rn | awk '{printf "  %8d  %s\n", $2, $1}'

