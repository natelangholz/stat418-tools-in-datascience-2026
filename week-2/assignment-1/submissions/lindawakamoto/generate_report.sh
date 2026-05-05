#!/bin/bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 data/NASA_Jul95.log data/NASA_Aug95.log"
  exit 1
fi

export LC_ALL=C
export LANG=C

JUL="$1"
AUG="$2"

REPORT="REPORT.md"

metrics() {
  awk '
  {
    total++

    host=$1
    code=$9
    url=$7
    ts=$4

    gsub(/\[/,"",ts)
    split(ts,a,":")
    split(a[1],date_parts,"/")

    day_key = date_parts[1] "/" date_parts[2] "/" date_parts[3]
    hour = a[2]

    day_count[day_key]++
    hour_count[hour]++

    if (code==404) err404++

    if (host ~ /^[0-9]/) ip++; else hostn++

    if (code!=404) {
      host_count[host]++
      url_count[url]++
    }
  }

  END {
    print total+0
    print err404+0
    print ip+0
    print hostn+0

    max=0; min=1e18
    for (dkey in day_count) {
      if (day_count[dkey]>max) {max=day_count[dkey]; busy=dkey}
      if (day_count[dkey]<min) {min=day_count[dkey]; quiet=dkey}
    }

    print busy
    print quiet

    maxh=0; minh=1e18
    for (h in hour_count) {
      if (hour_count[h]>maxh) {maxh=hour_count[h]; peak=h}
      if (hour_count[h]<minh) {minh=hour_count[h]; qh=h}
    }

    print peak
    print qh
  }
  '
}

run_metrics() {
  metrics < "$1"
}

read_metrics() {
  local file="$1"
  local lines=()

  while IFS= read -r line; do
    lines+=("$line")
  done < <(run_metrics "$file")

  if [[ ${#lines[@]} -lt 8 ]]; then
    echo "ERROR: Failed to parse metrics for $file"
    exit 1
  fi

  TOTAL="${lines[0]}"
  ERR404="${lines[1]}"
  IP="${lines[2]}"
  HOST="${lines[3]}"
  BUSY="${lines[4]}"
  QUIET="${lines[5]}"
  PEAK="${lines[6]}"
  QH="${lines[7]}"
}

# JULY
read_metrics "$JUL"
JUL_TOTAL="$TOTAL"
JUL_404="$ERR404"
JUL_IP="$IP"
JUL_HOST="$HOST"
JUL_BUSY="$BUSY"
JUL_QUIET="$QUIET"
JUL_PEAK="$PEAK"
JUL_QH="$QH"

# AUGUST
read_metrics "$AUG"
AUG_TOTAL="$TOTAL"
AUG_404="$ERR404"
AUG_IP="$IP"
AUG_HOST="$HOST"
AUG_BUSY="$BUSY"
AUG_QUIET="$QUIET"
AUG_PEAK="$PEAK"
AUG_QH="$QH"

scale() {
  awk -v v="$1" 'BEGIN {print (v<1?0:int(v/50000))}'
}

{
echo "# NASA Web Log Analysis Report"
echo ""
echo "_Generated: $(date)_"
echo ""

echo "## Summary"
echo "| Metric | July | August | Change |"
echo "|--------|------|--------|--------|"
echo "| Requests | $JUL_TOTAL | $AUG_TOTAL | $((AUG_TOTAL-JUL_TOTAL)) |"
echo "| 404 Errors | $JUL_404 | $AUG_404 | $((AUG_404-JUL_404)) |"
echo "| IP Requests | $JUL_IP | $AUG_IP | $((AUG_IP-JUL_IP)) |"
echo ""

echo "## Time Analysis"
echo "| Metric | July | August |"
echo "|--------|------|--------|"
echo "| Busiest Day | $JUL_BUSY | $AUG_BUSY |"
echo "| Quietest Day | $JUL_QUIET | $AUG_QUIET |"
echo "| Peak Hour | $JUL_PEAK | $AUG_PEAK |"
echo "| Quiet Hour | $JUL_QH | $AUG_QH |"
echo ""

echo "## Visualization"
printf "July   : "
for ((i=0;i<$(scale "$JUL_TOTAL");i++)); do printf "#"; done
echo ""

printf "August : "
for ((i=0;i<$(scale "$AUG_TOTAL");i++)); do printf "#"; done
echo ""

echo ""
echo "## Key Findings"
(( AUG_TOTAL > JUL_TOTAL )) && echo "- Traffic increased in August" || echo "- Traffic decreased in August"
(( AUG_404 > JUL_404 )) && echo "- Errors increased in August" || echo "- Errors decreased in August"

} > "$REPORT"

echo "Report written to: $REPORT"