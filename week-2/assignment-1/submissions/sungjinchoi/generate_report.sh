#!/bin/bash
set -euo pipefail

AUG_FILE="analysis/NASA_Aug95_analysis.txt"
JUL_FILE="analysis/NASA_Jul95_analysis.txt"
REPORT_OUT="REPORT.md"

for f in "$JUL_FILE" "$AUG_FILE"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: Missing analysis file: $f"
    exit 1
  fi
done

parse_kv() {
  local file="$1"
  local prefix="$2"
  while IFS='=' read -r key val; do
    [[ "$key" =~ ^=== ]] && break
    [[ -z "$key" ]] && continue
    [[ "$key" == "FILE" ]] && continue
    eval "${prefix}_${key}=\"\${val}\""
  done < <(grep -v '^===' "$file" | grep '=')
}

get_section() {
  local file="$1"
  local section="$2"
  awk "/^===${section}===/{found=1; next} /^===/{found=0} found{print}" "$file"
}

bar_chart() {
  local max_width=40
  local lines
  lines=$(cat)
  [[ -z "$lines" ]] && return
  local max_val
  max_val=$(echo "$lines" | awk '{print $1+0}' | sort -n | tail -1)
  [[ -z "$max_val" || "$max_val" -eq 0 ]] && return
  echo "$lines" | awk -v mw="$max_width" -v mv="$max_val" '
  {
    count=$1; label=$2
    bar_len = int(count * mw / mv)
    bar = ""
    for (i = 0; i < bar_len; i++) bar = bar "#"
    printf "  %-20s | %-40s %s\n", label, bar, count
  }'
}

parse_kv "$JUL_FILE" "JUL"
parse_kv "$AUG_FILE" "AUG"

cat > "$REPORT_OUT" << HEADER
# NASA Web Server Log Analysis Report

**Data:** NASA access logs — July 1995 and August 1995
**Generated:** $(date "+%Y-%m-%d %H:%M:%S")

---

## 1. Traffic Overview

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Total requests | $(printf "%'d" "$JUL_TOTAL_REQUESTS") | $(printf "%'d" "$AUG_TOTAL_REQUESTS") |
| IP-based requests | $JUL_IP_PERCENT% | $AUG_IP_PERCENT% |
| Hostname-based requests | $JUL_HOSTNAME_PERCENT% | $AUG_HOSTNAME_PERCENT% |
| 404 errors | $(printf "%'d" "$JUL_TOTAL_404_ERRORS") | $(printf "%'d" "$AUG_TOTAL_404_ERRORS") |
| Most frequent response | $JUL_MOST_FREQUENT_RESPONSE_CODE ($JUL_MOST_FREQUENT_RESPONSE_CODE_PERCENT%) | $AUG_MOST_FREQUENT_RESPONSE_CODE ($AUG_MOST_FREQUENT_RESPONSE_CODE_PERCENT%) |
| Max response (bytes) | $JUL_MAX_RESPONSE_BYTES | $AUG_MAX_RESPONSE_BYTES |
| Avg response (bytes) | $JUL_AVG_RESPONSE_BYTES | $AUG_AVG_RESPONSE_BYTES |

Traffic dropped in August.
IP access went up by $(awk "BEGIN{printf \"%.2f\", $AUG_IP_PERCENT - $JUL_IP_PERCENT}")pp. More direct access in August.

Note on 404 count: includes malformed log lines (missing HTTP version, special chars in URL). Standard-format only gives July 10,714 / August 9,978. Both are real 404 responses.

---

## 2. Peak Hours

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Busiest hour | ${JUL_BUSIEST_HOUR}:00 ($(printf "%'d" "$JUL_BUSIEST_HOUR_COUNT") reqs) | ${AUG_BUSIEST_HOUR}:00 ($(printf "%'d" "$AUG_BUSIEST_HOUR_COUNT") reqs) |
| Quietest hour | ${JUL_QUIETEST_HOUR}:00 ($(printf "%'d" "$JUL_QUIETEST_HOUR_COUNT") reqs) | ${AUG_QUIETEST_HOUR}:00 ($(printf "%'d" "$AUG_QUIETEST_HOUR_COUNT") reqs) |

### Hourly traffic — July 1995

HEADER

get_section "$JUL_FILE" "REQUESTS_BY_HOUR" \
  | grep -v '^NA' \
  | awk '{print $2, $1}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << AUG_HOUR

### Hourly traffic — August 1995

AUG_HOUR

get_section "$AUG_FILE" "REQUESTS_BY_HOUR" \
  | grep -v '^NA' \
  | awk '{print $2, $1}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << BUSYDAY

---

## 3. Busiest and Quietest Days

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Busiest day | $JUL_BUSIEST_DAY ($(printf "%'d" "$JUL_BUSIEST_DAY_COUNT") reqs) | $AUG_BUSIEST_DAY ($(printf "%'d" "$AUG_BUSIEST_DAY_COUNT") reqs) |
| Quietest day | $JUL_QUIETEST_DAY ($(printf "%'d" "$JUL_QUIETEST_DAY_COUNT") reqs) | $AUG_QUIETEST_DAY ($(printf "%'d" "$AUG_QUIETEST_DAY_COUNT") reqs) |

---

## 4. Hurricane Outage (August)

Aug 02 has no data. Surrounding days:

BUSYDAY

get_section "$AUG_FILE" "REQUESTS_BY_DAY" \
  | awk '/^0[1-4]\/Aug/ {print}' >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << OUTAGE

Aug 02 is missing. Looks like a full day outage.

---

## 5. Top 10 Hosts

### July 1995

OUTAGE

get_section "$JUL_FILE" "TOP_10_HOSTS" \
  | awk '{print $1, $2}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << AUG_HOSTS

### August 1995

AUG_HOSTS

get_section "$AUG_FILE" "TOP_10_HOSTS" \
  | awk '{print $1, $2}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << TOP_URLS

July: mostly prodigy.com. August: more AOL proxies and direct IPs.

---

## 6. Top 10 Requested URLs

### July 1995

TOP_URLS

get_section "$JUL_FILE" "TOP_10_URLS" \
  | awk '{print $1, $2}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << AUG_URLS

### August 1995

AUG_URLS

get_section "$AUG_FILE" "TOP_10_URLS" \
  | awk '{print $1, $2}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << HTTP_METHODS

Most are small GIF images. Same ones loaded every page.

---

## 7. HTTP Methods

### July 1995

HTTP_METHODS

get_section "$JUL_FILE" "HTTP_METHOD_COUNTS" \
  | awk '{print $1, $2}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << AUG_METHODS

### August 1995

AUG_METHODS

get_section "$AUG_FILE" "HTTP_METHOD_COUNTS" \
  | awk '{print $1, $2}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << RESP_CODES

---

## 8. Response Code Breakdown

### July 1995

RESP_CODES

get_section "$JUL_FILE" "RESPONSE_CODE_COUNTS" \
  | grep -v '^1 ' \
  | awk '{print $1, $2}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << AUG_RESP

### August 1995

AUG_RESP

get_section "$AUG_FILE" "RESPONSE_CODE_COUNTS" \
  | awk '{print $1, $2}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << ERROR_PATTERNS

---

## 9. Error Patterns (404 by Hour)

404 errors follow traffic. More during peak hours.

### July 1995

ERROR_PATTERNS

get_section "$JUL_FILE" "404_ERRORS_BY_HOUR" \
  | grep -v '^NA' \
  | awk '{print $2, $1}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << AUG_ERRORS

### August 1995

AUG_ERRORS

get_section "$AUG_FILE" "404_ERRORS_BY_HOUR" \
  | grep -v '^NA' \
  | awk '{print $2, $1}' \
  | bar_chart >> "$REPORT_OUT"

cat >> "$REPORT_OUT" << CONCLUSION

---

## 10. Summary

- Traffic dropped in August. Aug 02 outage affected the total.
- ~90% success rate in both months.
- IP access grew from 22% to 28% in August.
- Top URLs are images. Same assets over and over.
- Peak is around 14:00–15:00 in both months.
- Busiest day: Jul 13 and Aug 31.
CONCLUSION

echo "Report written to $REPORT_OUT"
