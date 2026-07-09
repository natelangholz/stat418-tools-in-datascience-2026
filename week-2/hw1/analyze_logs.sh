#!/bin/bash

# ensures pass of least one file
if [[ $# -eq 0 ]]; then
    echo "Usage: bash analyze_logs.sh <logfile>"
    exit 1
fi

LOGFILE="$1"

# ensure first argument passed exists
if [[ ! -f "$LOGFILE" ]]; then
    echo "ERROR: File '$LOGFILE' not found."
    exit 1
fi

echo "========================================"
echo " Analyzing: $LOGFILE"
echo "========================================"

# print host for when the status isn't a 404 error
# sorts hosts, counts consecutive duplicate lines
# sorts numerically in reverse
# keeps only first 10 lines
echo ""
echo "--- 1. Top 10 Hosts (excluding 404 errors) ---"
awk '$9 != 404 {print $1}' "$LOGFILE" \
    | sort | uniq -c | sort -rn | head -10
echo "DONE: section 1"

# skip blank lines
# count IP addresses with pattern

echo ""
echo "--- 2. IP vs Hostname percentage ---"
total=$(awk 'NF > 0 {print $1}' "$LOGFILE" | wc -l)
ip_count=$(awk '{print $1}' "$LOGFILE" \
    | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | wc -l)
hostname_count=$((total - ip_count))
ip_pct=$(awk "BEGIN {printf \"%.2f\", ($ip_count/$total)*100}")
host_pct=$(awk "BEGIN {printf \"%.2f\", ($hostname_count/$total)*100}")
echo "  Total requests : $total"
echo "  IP addresses   : $ip_count ($ip_pct%)"
echo "  Hostnames      : $hostname_count ($host_pct%)"
echo "DONE: section 2"

# find top 10 requests
echo ""
echo "--- 3. Top 10 Requested URLs (excluding 404 errors) ---"
awk '$9 != 404 {print $7}' "$LOGFILE" \
    | sort | uniq -c | sort -rn | head -10
echo "DONE: section 3"

# find most frequent request types
echo ""
echo "--- 4. HTTP Request Types ---"
awk '{print $6}' "$LOGFILE" \
    | tr -d '"' \
    | sort | uniq -c | sort -rn
echo "DONE: section 4"

echo ""
echo "--- 5. Total 404 Errors ---"
awk '$9 == 404' "$LOGFILE" | wc -l
echo "DONE: section 5"

echo ""
echo "--- 6. Most Frequent Response Code ---"
awk 'NF >= 9 {print $9}' "$LOGFILE" \
    | sort | uniq -c | sort -rn | head -5
total_responses=$(awk 'NF >= 9' "$LOGFILE" | wc -l)
top_code=$(awk 'NF >= 9 {print $9}' "$LOGFILE" \
    | sort | uniq -c | sort -rn | head -1)
top_count=$(echo "$top_code" | awk '{print $1}')
top_code_val=$(echo "$top_code" | awk '{print $2}')
top_pct=$(awk "BEGIN {printf \"%.2f\", ($top_count/$total_responses)*100}")
echo "  Most frequent: $top_code_val at $top_pct% of all responses"
echo "DONE: section 6"

echo ""
echo "--- 7. Requests by Hour of Day ---"
awk '{print $4}' "$LOGFILE" \
    | grep -oE ':[0-9]{2}:[0-9]{2}:[0-9]{2}' \
    | cut -d: -f2 \
    | sort | uniq -c | sort -k2 -n
echo "DONE: section 7"

echo ""
echo "--- 8. Busiest Day ---"
awk '{print $4}' "$LOGFILE" \
    | grep -oE '[0-9]{2}/[A-Za-z]+/[0-9]{4}' \
    | sort | uniq -c | sort -rn | head -1
echo "DONE: section 8"

echo ""
echo "--- 9. Quietest Day ---"
awk '{print $4}' "$LOGFILE" \
    | grep -oE '[0-9]{2}/[A-Za-z]+/[0-9]{4}' \
    | sort | uniq -c | sort -n | head -5
echo "DONE: section 9"

echo ""
echo "--- 10. Hurricane Outage Detection ---"
awk '{print $4}' "$LOGFILE" \
    | grep -oE '[0-9]{2}/[A-Za-z]+/[0-9]{4}:[0-9]{2}' \
    | sort | uniq -c \
    | awk '$1 < 100 {print "Possible gap: " $2 " (only " $1 " requests)"}'
echo "DONE: section 10"

echo ""
echo "--- 11. Largest and Average Response Size (bytes) ---"
awk 'NF >= 10 && $10 ~ /^[0-9]+$/ {
    if ($10 > max) max = $10
    total += $10
    count++
} END {
    printf "  Largest : %d bytes\n", max
    printf "  Average : %.0f bytes\n", total/count
}' "$LOGFILE"
echo "DONE: section 11"

echo ""
echo "--- 12. Error Patterns (top hours for errors) ---"
awk '$9 >= 400 {print $4}' "$LOGFILE" \
    | grep -oE ':[0-9]{2}:[0-9]{2}:[0-9]{2}' \
    | cut -d: -f2 \
    | sort | uniq -c | sort -rn | head -5
echo "DONE: section 12"

echo ""
echo "========================================"
echo " Analysis complete for: $LOGFILE"
echo "========================================"
