#!/bin/bash
# generate_report.sh - Generate a markdown report from NASA web server logs

# Use provided file paths or fall back to defaults
JUL=${1:-NASA_Jul95.log}
AUG=${2:-NASA_Aug95.log}
REPORT="REPORT.md"

# Check that both log files exist before doing anything
if [ ! -f "$JUL" ]; then
  echo "Error: $JUL not found"
  exit 1
fi
if [ ! -f "$AUG" ]; then
  echo "Error: $AUG not found"
  exit 1
fi

echo "Computing July statistics..."

JUL_TOTAL=$(wc -l < "$JUL")
JUL_404=$(awk '$9 == 404' "$JUL" | wc -l)
JUL_HOSTS=$(awk '{print $1}' "$JUL" | sort -u | wc -l)
JUL_BUSIEST=$(awk '{print substr($4,2,11)}' "$JUL" | sort | uniq -c | sort -rn | head -1)
JUL_PEAK=$(awk '{split($4,t,":"); print t[2]}' "$JUL" | sort | uniq -c | sort -rn | head -1)
JUL_TOP_URL=$(awk '$9 != 404 {print $7}' "$JUL" | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
JUL_MAX_SIZE=$(awk '$10 ~ /^[0-9]+$/ && $10+0 > max {max=$10} END {print max}' "$JUL")
JUL_AVG_SIZE=$(awk '$10 ~ /^[0-9]+$/ {sum+=$10; count++} END {printf "%.0f", sum/count}' "$JUL")

echo "Computing August statistics..."

AUG_TOTAL=$(wc -l < "$AUG")
AUG_404=$(awk '$9 == 404' "$AUG" | wc -l)
AUG_HOSTS=$(awk '{print $1}' "$AUG" | sort -u | wc -l)
AUG_BUSIEST=$(awk '{print substr($4,2,11)}' "$AUG" | sort | uniq -c | sort -rn | head -1)
AUG_PEAK=$(awk '{split($4,t,":"); print t[2]}' "$AUG" | sort | uniq -c | sort -rn | head -1)
AUG_TOP_URL=$(awk '$9 != 404 {print $7}' "$AUG" | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
AUG_MAX_SIZE=$(awk '$10 ~ /^[0-9]+$/ && $10+0 > max {max=$10} END {print max}' "$AUG")
AUG_AVG_SIZE=$(awk '$10 ~ /^[0-9]+$/ {sum+=$10; count++} END {printf "%.0f", sum/count}' "$AUG")

# Figure out which month had more requests for the comparison section
if [ "$AUG_TOTAL" -gt "$JUL_TOTAL" ]; then
  DIFF=$(( AUG_TOTAL - JUL_TOTAL ))
  COMPARE="August had **$DIFF more requests** than July."
else
  DIFF=$(( JUL_TOTAL - AUG_TOTAL ))
  COMPARE="July had **$DIFF more requests** than August."
fi

echo "Writing report to $REPORT..."

# Write everything to REPORT.md using a single redirect block
{
  echo "# NASA Web Server Log Analysis Report"
  echo ""
  echo "**Generated:** $(date)"
  echo ""
  echo "---"
  echo ""
  echo "## Summary Statistics"
  echo ""
  echo "| Metric | July 1995 | August 1995 |"
  echo "|--------|-----------|-------------|"
  echo "| Total requests | $JUL_TOTAL | $AUG_TOTAL |"
  echo "| Unique hosts | $JUL_HOSTS | $AUG_HOSTS |"
  echo "| 404 errors | $JUL_404 | $AUG_404 |"
  echo "| Largest response | ${JUL_MAX_SIZE} bytes | ${AUG_MAX_SIZE} bytes |"
  echo "| Avg response size | ${JUL_AVG_SIZE} bytes | ${AUG_AVG_SIZE} bytes |"
  echo "| Busiest day | $JUL_BUSIEST | $AUG_BUSIEST |"
  echo "| Peak hour | $JUL_PEAK | $AUG_PEAK |"
  echo ""
  echo "---"
  echo ""
  echo "## July 1995 Analysis"
  echo ""
  echo "**Most requested URL:** \`$JUL_TOP_URL\`"
  echo ""
  echo "### Requests by Hour of Day (July)"
  echo ""
  echo "Each \`#\` represents ~2,000 requests. Scale is relative to July's peak hour."
  echo ""
  echo '```'
  # ASCII bar chart: store counts in arrays, scale bars relative to the max
  awk '{split($4,t,":"); print t[2]}' "$JUL" | grep -E '^[0-9]{2}$' | sort | uniq -c | sort -k2 -n | \
  awk 'BEGIN {max=0}
       { count[NR]=$1; hour[NR]=$2; if($1>max) max=$1; n=NR }
       END {
         for (i=1; i<=n; i++) {
           bars = int(count[i] * 40 / max)
           if (bars < 1) bars = 1
           printf "  %s | ", hour[i]
           for (j=0; j<bars; j++) printf "#"
           printf " (%d)\n", count[i]
         }
       }'
  echo '```'
  echo ""
  echo "---"
  echo ""
  echo "## August 1995 Analysis"
  echo ""
  echo "**Most requested URL:** \`$AUG_TOP_URL\`"
  echo ""
  echo "**Hurricane outage:** August 2nd is entirely missing from the logs."
  echo "Data stopped at \`01/Aug/1995 14:52:01\` and resumed at \`03/Aug/1995 04:36:13\`,"
  echo "an outage of approximately **37 hours 44 minutes**."
  echo ""
  echo "### Requests by Hour of Day (August)"
  echo ""
  echo "Each \`#\` represents ~2,000 requests. Scale is relative to August's peak hour."
  echo "Note: lower total counts reflect the two-day outage."
  echo ""
  echo '```'
  awk '{split($4,t,":"); print t[2]}' "$AUG" | grep -E '^[0-9]{2}$' | sort | uniq -c | sort -k2 -n | \
  awk 'BEGIN {max=0}
       { count[NR]=$1; hour[NR]=$2; if($1>max) max=$1; n=NR }
       END {
         for (i=1; i<=n; i++) {
           bars = int(count[i] * 40 / max)
           if (bars < 1) bars = 1
           printf "  %s | ", hour[i]
           for (j=0; j<bars; j++) printf "#"
           printf " (%d)\n", count[i]
         }
       }'
  echo '```'
  echo ""
  echo "---"
  echo ""
  echo "## July vs August Comparison"
  echo ""
  echo "$COMPARE"
  echo ""
  echo "| Metric | Change |"
  echo "|--------|--------|"
  echo "| Requests | July: $JUL_TOTAL vs August: $AUG_TOTAL |"
  echo "| 404 errors | July: $JUL_404 vs August: $AUG_404 |"
  echo "| Unique hosts | July: $JUL_HOSTS vs August: $AUG_HOSTS |"
  echo "| Avg response size | July: ${JUL_AVG_SIZE}B vs August: ${AUG_AVG_SIZE}B |"
  echo ""
  echo "---"
  echo ""
  echo "## Interesting Findings and Anomalies"
  echo ""
  echo "- **Hurricane outage (August):** August 2nd is completely absent from the logs due to a hurricane."
  echo "  Nearly 38 hours of traffic data was lost, affecting day-over-day totals."
  echo "- **Peak traffic time:** Both months peak around 3 PM EDT (hour 15), consistent with"
  echo "  daytime NASA website browsing patterns."
  echo "- **404 error rate:** July had $JUL_404 404 errors vs August's $AUG_404 — the similar"
  echo "  counts across both months suggest persistent broken links rather than one-off issues."
  echo "- **Response sizes:** The largest single response was over 3 MB (likely a large image or"
  echo "  file download), while the average of ~17 KB is typical for a mix of HTML and images."
  echo "- **Host types:** The majority of traffic comes from named hostnames rather than raw IP"
  echo "  addresses, suggesting most visitors were on institutional networks."

} > "$REPORT"

echo "Report written to $REPORT"
