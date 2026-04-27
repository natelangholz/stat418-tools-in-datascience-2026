#!/bin/bash
# analyze_logs.sh - Analyze NASA web server log file
# Usage: ./analyze_logs.sh <log_file>
#
# Answers all 12 questions required by the assignment.
# Each section prints a header so that generate_report.sh can pull
# the pieces it needs.

# Note: we intentionally do NOT use `-o pipefail` here because several
# analysis pipelines end in `... | head -N` which closes the pipe early
# and causes upstream commands (sort/awk) to exit with SIGPIPE (141).
set -eu

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <log_file>" >&2
  exit 1
fi

LOGFILE="$1"

if [[ ! -f "$LOGFILE" ]]; then
  echo "Error: File not found: $LOGFILE" >&2
  exit 1
fi

echo "==========================================="
echo "Analyzing file: $LOGFILE"
echo "==========================================="
echo

# Log format reminder:
# host  -  -  [dd/Mon/yyyy:HH:MM:SS -0400]  "METHOD /url PROTOCOL"  status  bytes
#  $1   $2 $3         $4            $5       $6     $7      $8        $9    $10

total=$(wc -l < "$LOGFILE")
echo "Total log lines: $total"
echo

# -----------------------------------------------------------------------------
# 1. Top 10 hosts (excluding 404 errors)
# -----------------------------------------------------------------------------
echo "## 1. Top 10 hosts (excluding 404 errors)"
awk '$9 != 404 {print $1}' "$LOGFILE" \
  | sort | uniq -c | sort -nr | head -10
echo

# -----------------------------------------------------------------------------
# 2. IP vs Hostname percentage
# -----------------------------------------------------------------------------
echo "## 2. IP vs Hostname percentage"
ip_count=$(awk '{print $1}' "$LOGFILE" \
  | grep -Ec '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || true)
host_count=$((total - ip_count))
awk -v ip="$ip_count" -v host="$host_count" -v total="$total" 'BEGIN {
  if (total == 0) {
    print "IP requests:       0 (0.00%)"
    print "Hostname requests: 0 (0.00%)"
  } else {
    printf "IP requests:       %d (%.2f%%)\n", ip,   (ip/total)*100
    printf "Hostname requests: %d (%.2f%%)\n", host, (host/total)*100
  }
}'
echo

# -----------------------------------------------------------------------------
# 3. Top 10 most requested URLs (excluding 404 errors)
# -----------------------------------------------------------------------------
echo "## 3. Top 10 most requested URLs (excluding 404 errors)"
# Strip any stray quote characters from the URL field and require it to
# start with "/", so malformed requests don't leak into the top list.
awk '$9 != 404 {gsub(/"/, "", $7); if ($7 ~ /^\//) print $7}' "$LOGFILE" \
  | sort | uniq -c | sort -nr | head -10
echo

# -----------------------------------------------------------------------------
# 4. HTTP request methods
# -----------------------------------------------------------------------------
echo "## 4. HTTP methods (counts)"
# Filter to real HTTP methods only. Some log lines have malformed request
# fields (binary garbage, shifted columns, URLs in method position); we
# keep only tokens that are all uppercase letters after stripping quotes.
awk '{print $6}' "$LOGFILE" \
  | tr -d '"' \
  | grep -E '^[A-Z]+$' \
  | sort | uniq -c | sort -nr
echo

# -----------------------------------------------------------------------------
# 5. 404 error count
# -----------------------------------------------------------------------------
echo "## 5. 404 errors"
err404=$(awk '$9 == 404' "$LOGFILE" | wc -l)
awk -v e="$err404" -v t="$total" 'BEGIN {
  if (t == 0) {
    printf "404 errors: %d (0.00%% of all responses)\n", e
  } else {
    printf "404 errors: %d (%.2f%% of all responses)\n", e, (e/t)*100
  }
}'
echo

# -----------------------------------------------------------------------------
# 6. Most frequent response code
# -----------------------------------------------------------------------------
echo "## 6. Response code distribution"
# Only count rows whose status field is a valid 3-digit HTTP code.
# Some log lines have malformed requests that shift fields, so we filter
# out non-numeric / out-of-range values.
awk '$9 ~ /^[1-5][0-9][0-9]$/ {print $9}' "$LOGFILE" \
  | sort | uniq -c | sort -nr
echo
echo "Most frequent response code:"
awk '$9 ~ /^[1-5][0-9][0-9]$/ {print $9}' "$LOGFILE" \
  | sort | uniq -c | sort -nr | head -1 \
  | awk -v t="$total" '{
      if (t == 0) {
        printf "  code=%s  count=%d  percentage=0.00%%\n", $2, $1
      } else {
        printf "  code=%s  count=%d  percentage=%.2f%%\n", $2, $1, ($1/t)*100
      }
    }'
echo

# -----------------------------------------------------------------------------
# 7. Peak / quiet hours
# -----------------------------------------------------------------------------
echo "## 7. Activity by hour of day (24h)"
# $4 looks like [01/Jul/1995:00:00:01 -- split by ":" gives us the hour.
# We skip any lines with a malformed timestamp field.
awk '$4 ~ /^\[/ {split($4, a, ":"); print a[2]}' "$LOGFILE" \
  | sort | uniq -c | sort -k2,2n
echo
echo "Peak 3 hours:"
awk '$4 ~ /^\[/ {split($4,a,":"); print a[2]}' "$LOGFILE" \
  | sort | uniq -c | sort -nr | head -3
echo
echo "Quietest 3 hours:"
awk '$4 ~ /^\[/ {split($4,a,":"); print a[2]}' "$LOGFILE" \
  | sort | uniq -c | sort -n | head -3
echo

# -----------------------------------------------------------------------------
# 8. Busiest day
# -----------------------------------------------------------------------------
echo "## 8. Busiest day"
awk '$4 ~ /^\[/ {
  # strip leading "[" from $4, then keep only the dd/Mon/yyyy portion
  d = substr($4, 2)
  split(d, a, ":")
  print a[1]
}' "$LOGFILE" \
  | sort | uniq -c | sort -nr | head -1
echo

# -----------------------------------------------------------------------------
# 9. Quietest day (ignoring outage days which have zero entries in the log)
# -----------------------------------------------------------------------------
echo "## 9. Quietest day (with activity > 0)"
awk '$4 ~ /^\[/ {
  d = substr($4, 2); split(d, a, ":"); print a[1]
}' "$LOGFILE" \
  | sort | uniq -c | sort -n | head -1
echo

# -----------------------------------------------------------------------------
# 10. Outage detection (Hurricane Erin gap in August)
# -----------------------------------------------------------------------------
echo "## 10. Outage detection"
# Find the largest gap between successive log timestamps (in chronological
# order). Skips malformed lines whose $4 does not start with "[".
awk '$4 ~ /^\[/ {
  # $4 is like [01/Aug/1995:00:00:01
  t = substr($4, 2)               # 01/Aug/1995:00:00:01
  print t
}' "$LOGFILE" \
  | awk -F'[/:]' '
      BEGIN {
        mm["Jan"]=1; mm["Feb"]=2; mm["Mar"]=3; mm["Apr"]=4;
        mm["May"]=5; mm["Jun"]=6; mm["Jul"]=7; mm["Aug"]=8;
        mm["Sep"]=9; mm["Oct"]=10; mm["Nov"]=11; mm["Dec"]=12;
      }
      {
        # fields: 1=day 2=Mon 3=yyyy 4=HH 5=MM 6=SS
        ts = mktime(sprintf("%d %d %d %d %d %d",
                    $3, mm[$2], $1, $4, $5, $6))
        if (prev && ts - prev > max_gap) {
          max_gap   = ts - prev
          gap_start = prev_s
          gap_end_s = $1 "/" $2 "/" $3 " " $4 ":" $5 ":" $6
        }
        prev = ts
        prev_s = $1 "/" $2 "/" $3 " " $4 ":" $5 ":" $6
      }
      END {
        if (max_gap == "") {
          print "No gaps detected."
        } else {
          hrs = int(max_gap / 3600)
          mins = int((max_gap % 3600) / 60)
          secs = max_gap % 60
          printf "Largest gap: %s  ->  %s\n", gap_start, gap_end_s
          printf "Outage duration: %d seconds (%dh %dm %ds)\n", \
                  max_gap, hrs, mins, secs
        }
      }'
echo

# -----------------------------------------------------------------------------
# 11. Response size (max and average)
# -----------------------------------------------------------------------------
echo "## 11. Response size"
awk '$10 ~ /^[0-9]+$/ {
  if ($10 > max) max = $10
  sum += $10
  n++
}
END {
  if (n == 0) {
    print "No numeric response sizes found."
  } else {
    printf "Largest response: %d bytes\n", max
    printf "Average response: %.2f bytes\n", sum / n
    printf "Total bytes served: %d\n", sum
  }
}' "$LOGFILE"
echo

# -----------------------------------------------------------------------------
# 12. Error patterns: errors by hour and top hosts causing errors
# -----------------------------------------------------------------------------
echo "## 12. Error patterns"
echo "Errors (4xx/5xx) by hour of day:"
awk '$9 ~ /^[45]/ {split($4,a,":"); print a[2]}' "$LOGFILE" \
  | sort | uniq -c | sort -k2,2n
echo
echo "Top 10 hosts generating errors (4xx/5xx):"
awk '$9 ~ /^[45]/ {print $1}' "$LOGFILE" \
  | sort | uniq -c | sort -nr | head -10
echo
echo "Top 10 URLs producing errors:"
awk '$9 ~ /^[45]/ {gsub(/"/, "", $7); if ($7 ~ /^\//) print $7}' "$LOGFILE" \
  | sort | uniq -c | sort -nr | head -10
echo

echo "==========================================="
echo "Analysis complete for: $LOGFILE"
echo "==========================================="
