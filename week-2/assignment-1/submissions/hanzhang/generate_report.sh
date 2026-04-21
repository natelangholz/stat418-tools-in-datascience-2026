set -euo pipefail
export LC_ALL=C

ANALYSIS_DIR="${1:-analysis}"
REPORT_FILE="${2:-REPORT.md}"

if [[ ! -d "$ANALYSIS_DIR" ]]; then
  echo "ERROR: analysis directory not found: $ANALYSIS_DIR" >&2
  exit 1
fi

get_value() {
  local file="$1"
  local key="$2"
  awk -F= -v k="$key" '$1==k {print $2}' "$file"
}

append_table_from_counts() {
  local title="$1"
  local file="$2"
  {
    echo "### $title"
    echo
    echo "| Count | Value |"
    echo "|---:|---|"
    awk '{count=$1; $1=""; sub(/^ +/, "", $0); printf "| %s | %s |\n", count, $0}' "$file"
    echo
  } >> "$REPORT_FILE"
}

july_summary="$ANALYSIS_DIR/NASA_Jul95_summary.txt"
aug_summary="$ANALYSIS_DIR/NASA_Aug95_summary.txt"

if [[ ! -f "$july_summary" || ! -f "$aug_summary" ]]; then
  echo "ERROR: expected July and August summary files in $ANALYSIS_DIR" >&2
  exit 1
fi

july_total=$(get_value "$july_summary" total_requests)
aug_total=$(get_value "$aug_summary" total_requests)
july_404=$(get_value "$july_summary" 404_errors)
aug_404=$(get_value "$aug_summary" 404_errors)
july_ip_pct=$(get_value "$july_summary" ip_percentage)
aug_ip_pct=$(get_value "$aug_summary" ip_percentage)
july_peak=$(get_value "$july_summary" peak_hour)
aug_peak=$(get_value "$aug_summary" peak_hour)
july_busiest=$(get_value "$july_summary" busiest_day)
aug_busiest=$(get_value "$aug_summary" busiest_day)
aug_gap_s=$(get_value "$aug_summary" largest_gap_seconds)
aug_gap_start=$(get_value "$aug_summary" largest_gap_start)
aug_gap_end=$(get_value "$aug_summary" largest_gap_end)

{
  echo "# Assignment 1 Report: NASA Web Server Log Analysis"
  echo
  echo "Generated on: $(date)"
  echo
  echo "## Overview"
  echo
  echo "This report analyzes the NASA July and August 1995 web server logs using bash, grep, awk, sed, sort, uniq, and other command-line tools."
  echo
  echo "## Executive Summary"
  echo
  echo "- July total requests: **$july_total**"
  echo "- August total requests: **$aug_total**"
  echo "- July 404 errors: **$july_404**"
  echo "- August 404 errors: **$aug_404**"
  echo "- July IP-based requests: **${july_ip_pct}%**"
  echo "- August IP-based requests: **${aug_ip_pct}%**"
  echo "- July peak hour: **$july_peak:00**"
  echo "- August peak hour: **$aug_peak:00**"
  echo "- July busiest day: **$july_busiest**"
  echo "- August busiest day: **$aug_busiest**"
  echo
  echo "## July vs August Comparison"
  echo
  echo "| Metric | July | August |"
  echo "|---|---:|---:|"
  echo "| Total requests | $july_total | $aug_total |"
  echo "| 404 errors | $july_404 | $aug_404 |"
  echo "| IP request % | $july_ip_pct | $aug_ip_pct |"
  echo "| Peak hour | $july_peak | $aug_peak |"
  echo "| Busiest day | $july_busiest | $aug_busiest |"
  echo
  echo "## Hurricane Outage"
  echo
  echo "The longest gap in the August log appears to run from **$aug_gap_start** to **$aug_gap_end**."
  echo
  echo "- Gap length (seconds): **$aug_gap_s**"
  echo "- Gap length (hours): **$(awk -v s="$aug_gap_s" 'BEGIN{printf "%.2f", s/3600}')**"
  echo
  echo "This is a data-driven way to identify the outage period from the log timestamps."
  echo
  echo "## July Details"
  echo
} > "$REPORT_FILE"

append_table_from_counts "Top 10 Hosts (July, excluding 404s)" "$ANALYSIS_DIR/NASA_Jul95_top_hosts.txt"
append_table_from_counts "Top 10 Requests (July, excluding 404s)" "$ANALYSIS_DIR/NASA_Jul95_top_requests.txt"
append_table_from_counts "Request Types (July)" "$ANALYSIS_DIR/NASA_Jul95_request_types.txt"
append_table_from_counts "Response Codes (July)" "$ANALYSIS_DIR/NASA_Jul95_response_codes.txt"

{
  echo "### Hourly Activity (July)"
  echo
  echo '```text'
  cat "$ANALYSIS_DIR/NASA_Jul95_hourly_chart.txt"
  echo '```'
  echo
  echo "## August Details"
  echo
} >> "$REPORT_FILE"

append_table_from_counts "Top 10 Hosts (August, excluding 404s)" "$ANALYSIS_DIR/NASA_Aug95_top_hosts.txt"
append_table_from_counts "Top 10 Requests (August, excluding 404s)" "$ANALYSIS_DIR/NASA_Aug95_top_requests.txt"
append_table_from_counts "Request Types (August)" "$ANALYSIS_DIR/NASA_Aug95_request_types.txt"
append_table_from_counts "Response Codes (August)" "$ANALYSIS_DIR/NASA_Aug95_response_codes.txt"

{
  echo "### Hourly Activity (August)"
  echo
  echo '```text'
  cat "$ANALYSIS_DIR/NASA_Aug95_hourly_chart.txt"
  echo '```'
  echo
  echo "## Interesting Findings / Anomalies"
  echo
  echo "- August contains a very large timestamp gap, which is consistent with the hurricane outage prompt in the assignment."
  echo "- The report compares request volume, 404 counts, request composition, and peak traffic timing across both months."
  echo "- ASCII charts were included to keep the report reproducible and terminal-friendly."
  echo
} >> "$REPORT_FILE"

echo "Generated $REPORT_FILE"
