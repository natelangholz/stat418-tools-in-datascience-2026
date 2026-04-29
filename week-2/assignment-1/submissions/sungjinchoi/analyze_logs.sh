#!/bin/bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <logfile1> [logfile2 ...]"
  exit 1
fi

OUT_DIR="analysis"
mkdir -p "$OUT_DIR"

for LOGFILE in "$@"; do
  if [[ ! -f "$LOGFILE" ]]; then
    echo "ERROR: File not found: $LOGFILE"
    exit 1
  fi

  BASENAME=$(basename "$LOGFILE" .log)
  OUTFILE="$OUT_DIR/${BASENAME}_analysis.txt"

  awk -v filename="$LOGFILE" '
  function is_ip(host) {
    return host ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/
  }
  function get_hour(rawtime) {
    split(rawtime, a, ":")
    if (length(a) >= 2) return a[2]
    return "NA"
  }
  function get_day(rawtime) {
    split(rawtime, a, ":")
    return a[1]
  }
  {
    host = $1
    rawtime = $4
    gsub(/^\[/, "", rawtime)

    method = "UNKNOWN"
    url = "UNKNOWN"
    if (match($0, /\"[A-Z]+ [^ ]+ HTTP\/[0-9.]+\"/)) {
      req = substr($0, RSTART + 1, RLENGTH - 2)
      split(req, reqparts, " ")
      method = reqparts[1]
      url = reqparts[2]
    }

    status = $(NF-1)
    bytes = $NF
    if (bytes == "-") bytes = 0

    total++
    status_count[status]++
    method_count[method]++

    hour = get_hour(rawtime)
    day = get_day(rawtime)
    hour_count[hour]++
    day_count[day]++

    if (is_ip(host)) ip_count++
    else host_count++

    if (status == 404) {
      errors404++
      error_hour[hour]++
      error_host[host]++
    } else {
      host_hits[host]++
      url_hits[url]++
    }

    if (bytes ~ /^[0-9]+$/) {
      total_bytes += bytes+0
      if (bytes+0 > max_bytes) max_bytes = bytes+0
    }
  }
  END {
    print "FILE=" filename
    print "TOTAL_REQUESTS=" total
    print "IP_REQUESTS=" ip_count
    print "HOSTNAME_REQUESTS=" host_count
    print "IP_PERCENT=" sprintf("%.2f", ip_count * 100 / total)
    print "HOSTNAME_PERCENT=" sprintf("%.2f", host_count * 100 / total)
    print "TOTAL_404_ERRORS=" errors404

    max_code = ""
    max_code_count = -1
    for (c in status_count) {
      if (status_count[c] > max_code_count) {
        max_code_count = status_count[c]
        max_code = c
      }
    }
    print "MOST_FREQUENT_RESPONSE_CODE=" max_code
    print "MOST_FREQUENT_RESPONSE_CODE_COUNT=" max_code_count
    print "MOST_FREQUENT_RESPONSE_CODE_PERCENT=" sprintf("%.2f", max_code_count * 100 / total)

    print "MAX_RESPONSE_BYTES=" max_bytes
    print "AVG_RESPONSE_BYTES=" sprintf("%.2f", total_bytes / total)

    busiest_hour = ""
    quiet_hour = ""
    max_hour = -1
    min_hour = -1
    for (h in hour_count) {
      if (h == "NA" || h == "") continue
      if (hour_count[h] > max_hour) {
        max_hour = hour_count[h]
        busiest_hour = h
      }
      if (min_hour == -1 || hour_count[h] < min_hour) {
        min_hour = hour_count[h]
        quiet_hour = h
      }
    }
    print "BUSIEST_HOUR=" busiest_hour
    print "BUSIEST_HOUR_COUNT=" max_hour
    print "QUIETEST_HOUR=" quiet_hour
    print "QUIETEST_HOUR_COUNT=" min_hour

    busiest_day = ""
    quiet_day = ""
    max_day = -1
    min_day = -1
    for (d in day_count) {
      if (d == "") continue
      if (day_count[d] > max_day) {
        max_day = day_count[d]
        busiest_day = d
      }
      if (min_day == -1 || day_count[d] < min_day) {
        min_day = day_count[d]
        quiet_day = d
      }
    }
    print "BUSIEST_DAY=" busiest_day
    print "BUSIEST_DAY_COUNT=" max_day
    print "QUIETEST_DAY=" quiet_day
    print "QUIETEST_DAY_COUNT=" min_day

    print "===TOP_10_HOSTS==="
    for (h in host_hits) print host_hits[h], h | "sort -nr | head -10"
    close("sort -nr | head -10")

    print "===TOP_10_URLS==="
    for (u in url_hits) print url_hits[u], u | "sort -nr | head -10"
    close("sort -nr | head -10")

    print "===HTTP_METHOD_COUNTS==="
    for (m in method_count) print method_count[m], m | "sort -nr"
    close("sort -nr")

    print "===RESPONSE_CODE_COUNTS==="
    for (s in status_count) print status_count[s], s | "sort -nr"
    close("sort -nr")

    print "===REQUESTS_BY_HOUR==="
    for (h in hour_count) if (h != "NA" && h != "") print h, hour_count[h] | "sort"
    close("sort")

    print "===REQUESTS_BY_DAY==="
    for (d in day_count) if (d != "") print d, day_count[d] | "sort"
    close("sort")

    print "===404_ERRORS_BY_HOUR==="
    for (h in error_hour) print h, error_hour[h] | "sort"
    close("sort")
  }' "$LOGFILE" > "$OUTFILE"

  echo "===OUTAGE_GAPS===" >> "$OUTFILE"
  awk '/^===REQUESTS_BY_DAY===/{f=1;next} /^===/{f=0} f&&NF{print $1}' "$OUTFILE" | \
  sort | \
  awk '
  {
    split($1, a, "/")
    day = a[1]+0; mon = a[2]; yr = a[3]
    key = mon yr
    if (prev_key == key) {
      for (d = prev_day+1; d < day; d++) {
        printf "%02d/%s/%s MISSING\n", d, mon, yr
      }
    }
    prev_day = day; prev_key = key; prev_mon = mon; prev_yr = yr
  }' >> "$OUTFILE"

  echo "Created: $OUTFILE"
done