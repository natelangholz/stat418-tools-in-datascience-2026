#!/bin/bash
set -u

DATA_DIR="data"
ANALYSIS_DIR="analysis"
REPORT_FILE="REPORT.md"

JULY_ANALYSIS="$ANALYSIS_DIR/july_analysis.txt"
AUG_ANALYSIS="$ANALYSIS_DIR/august_analysis.txt"
JULY_LOG="$DATA_DIR/NASA_Jul95.log"
AUG_LOG="$DATA_DIR/NASA_Aug95.log"

if [[ ! -f "$JULY_ANALYSIS" || ! -f "$AUG_ANALYSIS" ]]; then
  echo "ERROR: Analysis files not found. Run analyze_logs.sh first."
  exit 1
fi

if [[ ! -f "$JULY_LOG" || ! -f "$AUG_LOG" ]]; then
  echo "ERROR: Log files not found. Run download_data.sh first."
  exit 1
fi

get_next_line() {
  local pattern="$1"
  local file="$2"
  awk -v pat="$pattern" '
    $0 ~ pat { getline; print; exit }
  ' "$file"
}

get_line_matching() {
  local pattern="$1"
  local file="$2"
  grep -m 1 "$pattern" "$file"
}

make_bar() {
  local value=$1
  local max=$2
  local width=40

  if [[ "$max" -eq 0 ]]; then
    printf ""
    return
  fi

  local bar_len=$(( value * width / max ))
  local bar=""

  for ((i=0; i<bar_len; i++)); do
    bar="${bar}#"
  done

  printf "%s" "$bar"
}

# Total requests directly from log files
JULY_TOTAL=$(wc -l < "$JULY_LOG")
AUG_TOTAL=$(wc -l < "$AUG_LOG")

# Pull summary stats from analysis files
JULY_404=$(get_next_line "^5\\. Number of 404 errors:" "$JULY_ANALYSIS")
AUG_404=$(get_next_line "^5\\. Number of 404 errors:" "$AUG_ANALYSIS")

JULY_PEAK=$(awk '/^7\. Peak hour\(s\):/ { getline; if ($0 == "") getline; print; exit }' "$JULY_ANALYSIS")
AUG_PEAK=$(awk '/^7\. Peak hour\(s\):/ { getline; if ($0 == "") getline; print; exit }' "$AUG_ANALYSIS")

JULY_BUSY=$(get_next_line "^8\\. Busiest day:" "$JULY_ANALYSIS")
AUG_BUSY=$(get_next_line "^8\\. Busiest day:" "$AUG_ANALYSIS")

JULY_QUIET=$(get_next_line "^9\\. Quietest day" "$JULY_ANALYSIS")
AUG_QUIET=$(get_next_line "^9\\. Quietest day" "$AUG_ANALYSIS")

JULY_CODE=$(awk -F': ' '/^Most frequent response code:/ { print $2; exit }' "$JULY_ANALYSIS")
AUG_CODE=$(awk -F': ' '/^Most frequent response code:/ { print $2; exit }' "$AUG_ANALYSIS")

JULY_CODE_COUNT=$(awk -F': ' '/^Count:/ { print $2; exit }' "$JULY_ANALYSIS")
AUG_CODE_COUNT=$(awk -F': ' '/^Count:/ { print $2; exit }' "$AUG_ANALYSIS")

JULY_CODE_PCT=$(awk -F': ' '/^Percentage:/ { print $2; exit }' "$JULY_ANALYSIS")
AUG_CODE_PCT=$(awk -F': ' '/^Percentage:/ { print $2; exit }' "$AUG_ANALYSIS")

JULY_SIZE_MAX=$(awk '/^Largest response size:/ { print $4 " bytes"; exit }' "$JULY_ANALYSIS")
AUG_SIZE_MAX=$(awk '/^Largest response size:/ { print $4 " bytes"; exit }' "$AUG_ANALYSIS")

JULY_SIZE_AVG=$(awk '/^Average response size:/ { print $4 " bytes"; exit }' "$JULY_ANALYSIS")
AUG_SIZE_AVG=$(awk '/^Average response size:/ { print $4 " bytes"; exit }' "$AUG_ANALYSIS")

AUG_OUTAGE_1=$(awk '/^10\. Hurricane outage/ {getline; print; exit}' "$AUG_ANALYSIS")
AUG_OUTAGE_2=$(awk '/^10\. Hurricane outage/ {getline; getline; print; exit}' "$AUG_ANALYSIS")
AUG_OUTAGE_3=$(awk '/^10\. Hurricane outage/ {getline; getline; getline; print; exit}' "$AUG_ANALYSIS")

# Numeric values for charts
MAX_TOTAL=$JULY_TOTAL
if [[ "$AUG_TOTAL" -gt "$MAX_TOTAL" ]]; then
  MAX_TOTAL=$AUG_TOTAL
fi

MAX_404=$JULY_404
if [[ "$AUG_404" -gt "$MAX_404" ]]; then
  MAX_404=$AUG_404
fi

# Extract numeric average response sizes
JULY_AVG_NUM=$(echo "$JULY_SIZE_AVG" | awk '{print int($1)}')
AUG_AVG_NUM=$(echo "$AUG_SIZE_AVG" | awk '{print int($1)}')

MAX_AVG=$JULY_AVG_NUM
if [[ "$AUG_AVG_NUM" -gt "$MAX_AVG" ]]; then
  MAX_AVG=$AUG_AVG_NUM
fi

# Compare activity
if [[ "$JULY_TOTAL" -gt "$AUG_TOTAL" ]]; then
  MORE_ACTIVITY="July had more total requests than August."
else
  MORE_ACTIVITY="August had more total requests than July."
fi

if [[ "$JULY_404" -gt "$AUG_404" ]]; then
  MORE_404="July had more 404 errors than August."
else
  MORE_404="August had more 404 errors than July."
fi

cat > "$REPORT_FILE" << EOF
# NASA Web Server Log Analysis Report

## Overview
This report summarizes the analysis of NASA web server logs for **July 1995** and **August 1995**.  
The goal was to compare traffic patterns, errors, request behavior, and unusual events across the two months.

## Summary Statistics

| Metric | July 1995 | August 1995 |
|---|---:|---:|
| Total requests | $JULY_TOTAL | $AUG_TOTAL |
| 404 errors | $JULY_404 | $AUG_404 |
| Peak hour | $JULY_PEAK | $AUG_PEAK |
| Busiest day | $JULY_BUSY | $AUG_BUSY |
| Quietest day | $JULY_QUIET | $AUG_QUIET |
| Most frequent response code | $JULY_CODE | $AUG_CODE |
| Response code count | $JULY_CODE_COUNT | $AUG_CODE_COUNT |
| Response code percentage | $JULY_CODE_PCT | $AUG_CODE_PCT |
| Largest response size | $JULY_SIZE_MAX | $AUG_SIZE_MAX |
| Average response size | $JULY_SIZE_AVG | $AUG_SIZE_AVG |

## July vs August Comparison

- $MORE_ACTIVITY
- $MORE_404
- July peak activity occurred at **$JULY_PEAK**.
- August peak activity occurred at **$AUG_PEAK**.
- July busiest day was **$JULY_BUSY**.
- August busiest day was **$AUG_BUSY**.
- August includes a major outage event that does not appear in July.

## Hurricane Outage in August

The August log shows a major gap in data collection:

- $AUG_OUTAGE_1
- $AUG_OUTAGE_2
- $AUG_OUTAGE_3

This outage is likely related to the hurricane event mentioned in the assignment.

## ASCII Visualizations

### Total Requests
- July   | $(make_bar "$JULY_TOTAL" "$MAX_TOTAL") $JULY_TOTAL
- August | $(make_bar "$AUG_TOTAL" "$MAX_TOTAL") $AUG_TOTAL

### 404 Errors
- July   | $(make_bar "$JULY_404" "$MAX_404") $JULY_404
- August | $(make_bar "$AUG_404" "$MAX_404") $AUG_404

### Average Response Size
- July   | $(make_bar "$JULY_AVG_NUM" "$MAX_AVG") $JULY_AVG_NUM bytes
- August | $(make_bar "$AUG_AVG_NUM" "$MAX_AVG") $AUG_AVG_NUM bytes

## Top 10 Hosts

### July 1995
\`\`\`
$(awk '
/^1\. Top 10 hosts\/IPs making requests/ {flag=1; next}
/^2\./ {flag=0}
flag
' "$JULY_ANALYSIS")
\`\`\`

### August 1995
\`\`\`
$(awk '
/^1\. Top 10 hosts\/IPs making requests/ {flag=1; next}
/^2\./ {flag=0}
flag
' "$AUG_ANALYSIS")
\`\`\`

## Top 10 Requested URLs

### July 1995
\`\`\`
$(awk '
/^3\. Top 10 most requested URLs/ {flag=1; next}
/^4\./ {flag=0}
flag
' "$JULY_ANALYSIS")
\`\`\`

### August 1995
\`\`\`
$(awk '
/^3\. Top 10 most requested URLs/ {flag=1; next}
/^4\./ {flag=0}
flag
' "$AUG_ANALYSIS")
\`\`\`

## Request Methods

### July 1995
\`\`\`
$(awk '
/^4\. HTTP request methods with counts:/ {flag=1; next}
/^5\./ {flag=0}
flag
' "$JULY_ANALYSIS")
\`\`\`

### August 1995
\`\`\`
$(awk '
/^4\. HTTP request methods with counts:/ {flag=1; next}
/^5\./ {flag=0}
flag
' "$AUG_ANALYSIS")
\`\`\`

## Interesting Findings

1. The vast majority of requests in both months received response code **200**, showing that most requests were successful.
2. Image files such as NASA logos and KSC logos were among the most frequently requested resources.
3. GET was by far the dominant HTTP method, while HEAD and POST were much less common.
4. August contained a clear outage, shown by the long time gap in the logs.
5. Traffic was concentrated in daytime and afternoon hours, while early morning hours were much quieter.

## Conclusion

Overall, both months show heavy web activity with similar request patterns, but **August stands out because of the outage event**.  
The logs also show that NASA image assets and homepage-related files were highly requested, and most traffic came through successful GET requests.

## Appendix: Full July Analysis

\`\`\`
$(cat "$JULY_ANALYSIS")
\`\`\`

## Appendix: Full August Analysis

\`\`\`
$(cat "$AUG_ANALYSIS")
\`\`\`
EOF

echo "Generated $REPORT_FILE successfully."