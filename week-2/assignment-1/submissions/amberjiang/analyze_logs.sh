#!/bin/bash
# analyze_logs.sh - Analyze logs

for FILE in "$@"; do
  echo "========================================"
  echo "Analyzing $FILE"
  echo "========================================"

  TOTAL=$(wc -l < "$FILE")

  echo
  echo "1. Top 10 hosts/IPs (excluding 404 errors):"
  awk '$9 != 404 {print $1}' "$FILE" | sort | uniq -c | sort -rn | head -10 | awk '{print $2}'

  echo
  echo "BASIC ANALYSIS:"

  echo
  echo "2. IP vs hostname requests:"
  IPS=$(awk '{print $1}' "$FILE" | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | wc -l)
  HOSTS=$((TOTAL - IPS))
  awk -v ips="$IPS" -v hosts="$HOSTS" -v total="$TOTAL" '
    BEGIN {
      printf "IP addresses: %d (%.2f%%)\n", ips, (ips/total)*100
      printf "Hostnames: %d (%.2f%%)\n", hosts, (hosts/total)*100
    }'

  echo
  echo "3. Top 10 requested URLs (excluding 404 errors):"
  awk '$9 != 404 {print $7}' "$FILE" | sort | uniq -c | sort -rn | head -10

  echo
  echo "4. Most frequent request types:"
  awk '{gsub(/"/, "", $6); print $6}' "$FILE" | sort | uniq -c | sort -rn

  echo
  echo "5.404 errors:"
  awk '$9 == 404' "$FILE" | wc -l

  echo
  echo "6. Most frequent response code:"
  awk '{print $9}' "$FILE" | sort | uniq -c | sort -rn | head -1 | \
  awk -v total="$TOTAL" '{printf "Code %s occurred %d times (%.2f%%)\n", $2, $1, ($1/total)*100}'

  echo  
  echo "TIME-BASED ANALYSIS:"

  echo
  echo "7. Peak and quiet hours:"
  echo "Peak hour:"
  awk '
    {
      split($4, t, ":")
      print t[2]
    }
  ' "$FILE" | sort | uniq -c | sort -rn | head -1
  echo "Quietest hour:"
  awk '
    {
      split($4, t, ":")
      print t[2]
    }
  ' "$FILE" | sort | uniq -c | sort -n | head -1

  echo
  echo "8. Busiest day:"
  awk '
    {
      d = substr($4, 2, 11)
      print d
    }
  ' "$FILE" | sort | uniq -c | sort -rn | head -1

  # Precompute outage info (used by Q9 and Q10)
  # Find which day numbers appear in the log, then find any missing day
  PRESENT_DAYS=$(awk '{print substr($4, 2, 2)+0}' "$FILE" | sort -n | uniq)
  MISSING_DAY=""
  OUTAGE_BEFORE=""
  OUTAGE_AFTER=""
  for DAY in $(seq 1 31); do
    if ! echo "$PRESENT_DAYS" | grep -qx "$DAY"; then
      MISSING_DAY=$DAY
      OUTAGE_BEFORE=$(( DAY - 1 ))
      OUTAGE_AFTER=$(( DAY + 1 ))
    fi
  done

  echo
  echo "9. Quietest day (excluding outage dates):"
  # If there is an outage, skip the missing day and its two partial neighbors
  if [ -n "$MISSING_DAY" ]; then
    awk -v skip1="$OUTAGE_BEFORE" -v skip2="$MISSING_DAY" -v skip3="$OUTAGE_AFTER" '
      {
        day = substr($4, 2, 2) + 0
        d = substr($4, 2, 11)
        if (day != skip1 && day != skip2 && day != skip3) print d
      }
    ' "$FILE" | sort | uniq -c | sort -n | head -1
  else
    awk '{print substr($4, 2, 11)}' "$FILE" | sort | uniq -c | sort -n | head -1
  fi

  echo
  echo "ADVANCED ANALYSIS:"

  echo
  echo "10. Hurricane outage (missing dates in this log):"
  if [ -n "$MISSING_DAY" ]; then
    # Find the last entry of the day before the gap and first entry of the day after
    LAST_BEFORE=$(awk -v d="$OUTAGE_BEFORE" '{day=substr($4,2,2)+0; if(day==d) print substr($4,2,20)}' "$FILE" | sort | tail -1)
    FIRST_AFTER=$(awk -v d="$OUTAGE_AFTER" '{day=substr($4,2,2)+0; if(day==d) print substr($4,2,20)}' "$FILE" | sort | head -1)
    echo "Last log entry before outage: $LAST_BEFORE"
    echo "First log entry after outage: $FIRST_AFTER"
    echo "Missing day(s):"
    for DAY in $(seq 1 31); do
      if ! echo "$PRESENT_DAYS" | grep -qx "$DAY"; then
        echo "  Day $DAY of the month (entire day missing)"
      fi
    done
    # Compute outage duration dynamically
    START=$(echo "$LAST_BEFORE" | sed 's|/| |g; s/:/ /')
    END=$(echo "$FIRST_AFTER" | sed 's|/| |g; s/:/ /')
    START_SEC=$(date -d "$START" +%s 2>/dev/null)
    END_SEC=$(date -d "$END" +%s 2>/dev/null)
    DIFF=$(( END_SEC - START_SEC ))
    HOURS=$(( DIFF / 3600 ))
    MINS=$(( (DIFF % 3600) / 60 ))
    echo "Outage duration: ~${HOURS} hours ${MINS} minutes"
  else
    echo "No outage detected in this log file"
  fi

  echo
  echo "11. Response sizes:"
  awk '$10 ~ /^[0-9]+$/ {
    if ($10+0 > max) { max=$10; maxline=$0 }
    sum += $10
    count++
  }
  END {
    printf "Largest response: %d bytes\n", max
    printf "Average response size: %.0f bytes\n", sum/count
  }' "$FILE"

  echo
  echo "12. Error patterns (4xx and 5xx status codes):"
  echo "Errors by hour of day:"
  awk '$9 ~ /^[45]/ {
    split($4, t, ":")
    print t[2]
  }' "$FILE" | sort | uniq -c | sort -rn | head -5 | \
  awk '{printf "  Hour %s: %d errors\n", $2, $1}'
  echo "Top 5 hosts with errors:"
  awk '$9 ~ /^[45]/ {print $1}' "$FILE" | sort | uniq -c | sort -rn | head -5 | \
  awk '{printf "  %s: %d errors\n", $2, $1}'

done

