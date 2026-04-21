
set -euo pipefail
export LC_ALL=C

INPUT="${1:-}"
OUT_DIR="${2:-analysis}"

if [[ -z "$INPUT" ]]; then
  echo "Usage: $0 <log_file> [out_dir]" >&2
  exit 1
fi

if [[ ! -f "$INPUT" ]]; then
  echo "ERROR: file not found: $INPUT" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

BASENAME="$(basename "$INPUT" .log)"
SUMMARY_FILE="$OUT_DIR/${BASENAME}_summary.txt"

awk -v base="$BASENAME" '
BEGIN{
  ip_re="^([0-9]{1,3}\\.){3}[0-9]{1,3}$"
}
NF{
  total++
  host=$1
  dt=$4
  gsub("\\[","",dt)
  split(dt, dparts, ":")
  daymonyear=dparts[1]
  hour=dparts[2]

  status=$(NF-1)
  bytes=$NF
  if (bytes == "-") bytes=0

  if (host ~ ip_re) ip_count++
  else host_count++

  if (status != 404) hosts[host]++
  status_counts[status]++
  hour_counts[hour]++
  day_counts[daymonyear]++

  if (status == 404) {
    err404++
    err404_hour[hour]++
    err404_host[host]++
  }

  if (status ~ /^5/) {
    err5xx++
    err5xx_hour[hour]++
    err5xx_host[host]++
  }

  total_bytes += bytes
  if (bytes > max_bytes) max_bytes = bytes

  ts = dparts[1] " " dparts[2] ":" dparts[3] ":" dparts[4]
  timestamps[++n_ts] = ts
  epochs[n_ts] = to_epoch(dparts[1], dparts[2], dparts[3], dparts[4])
}
END{
  ip_pct=(total>0)?(100*ip_count/total):0
  host_pct=(total>0)?(100*host_count/total):0

  max_status_count=0
  max_status=""
  for (s in status_counts) {
    if (status_counts[s] > max_status_count) {
      max_status_count=status_counts[s]
      max_status=s
    }
  }
  max_status_pct=(total>0)?(100*max_status_count/total):0

  peak_hour=""
  quiet_hour=""
  peak_hour_count=-1
  quiet_hour_count=-1
  for (h in hour_counts) {
    if (hour_counts[h] > peak_hour_count) {
      peak_hour_count=hour_counts[h]
      peak_hour=h
    }
    if (quiet_hour_count == -1 || hour_counts[h] < quiet_hour_count) {
      quiet_hour_count=hour_counts[h]
      quiet_hour=h
    }
  }

  busiest_day=""
  quietest_day=""
  busiest_count=-1
  quietest_count=-1
  for (d in day_counts) {
    if (day_counts[d] > busiest_count) {
      busiest_count=day_counts[d]
      busiest_day=d
    }
    if (quietest_count == -1 || day_counts[d] < quietest_count) {
      quietest_count=day_counts[d]
      quietest_day=d
    }
  }

  largest_gap=0
  gap_start=""
  gap_end=""
  for (i=2; i<=n_ts; i++) {
    gap=epochs[i]-epochs[i-1]
    if (gap > largest_gap) {
      largest_gap=gap
      gap_start=timestamps[i-1]
      gap_end=timestamps[i]
    }
  }

  avg_bytes=(total>0)?(total_bytes/total):0

  print "file=" base
  print "total_requests=" total
  print "ip_requests=" ip_count
  print "hostname_requests=" host_count
  printf "ip_percentage=%.2f\n", ip_pct
  printf "hostname_percentage=%.2f\n", host_pct
  print "404_errors=" err404
  print "5xx_errors=" err5xx
  print "max_response_bytes=" max_bytes
  printf "avg_response_bytes=%.2f\n", avg_bytes
  print "most_frequent_status=" max_status
  print "most_frequent_status_count=" max_status_count
  printf "most_frequent_status_percentage=%.2f\n", max_status_pct
  print "peak_hour=" peak_hour
  print "peak_hour_count=" peak_hour_count
  print "quiet_hour=" quiet_hour
  print "quiet_hour_count=" quiet_hour_count
  print "busiest_day=" busiest_day
  print "busiest_day_count=" busiest_count
  print "quietest_day_raw=" quietest_day
  print "quietest_day_raw_count=" quietest_count
  print "largest_gap_seconds=" largest_gap
  print "largest_gap_start=" gap_start
  print "largest_gap_end=" gap_end

  top404h=""
  top404hc=-1
  for (h in err404_hour) {
    if (err404_hour[h] > top404hc) {
      top404hc=err404_hour[h]
      top404h=h
    }
  }

  top404host=""
  top404hostc=-1
  for (x in err404_host) {
    if (err404_host[x] > top404hostc) {
      top404hostc=err404_host[x]
      top404host=x
    }
  }

  print "top_404_hour=" top404h
  print "top_404_hour_count=" top404hc
  print "top_404_host=" top404host
  print "top_404_host_count=" top404hostc
}
function monnum(mon) {
  return (mon=="Jan"?1:mon=="Feb"?2:mon=="Mar"?3:mon=="Apr"?4:mon=="May"?5:mon=="Jun"?6:mon=="Jul"?7:mon=="Aug"?8:mon=="Sep"?9:mon=="Oct"?10:mon=="Nov"?11:12)
}
function to_epoch(daymonyear, hour, min, sec,   day, mon, year, month) {
  day=substr(daymonyear,1,2)+0
  mon=substr(daymonyear,4,3)
  year=substr(daymonyear,8,4)+0
  month=monnum(mon)
  return mktime(sprintf("%04d %02d %02d %02d %02d %02d", year, month, day, hour, min, sec))
}
' "$INPUT" > "$SUMMARY_FILE"


awk '$(NF-1)!=404 {print $1}' "$INPUT" | sort | uniq -c | sort -rn | awk 'NR<=10' > "$OUT_DIR/${BASENAME}_top_hosts.txt"


awk -F'"' '$(NF-1)!=404 && $2 != "" {
  split($2, req, " ")
  if (req[2] != "") print req[2]
}' "$INPUT" | sort | uniq -c | sort -rn | awk 'NR<=10' > "$OUT_DIR/${BASENAME}_top_requests.txt"


awk '
match($0, /"([A-Z]+) /, a) {print a[1]; next}
{print "UNKNOWN"}
' "$INPUT" | sort | uniq -c | sort -rn > "$OUT_DIR/${BASENAME}_request_types.txt"


awk '$(NF-1) ~ /^[0-9][0-9][0-9]$/ {print $(NF-1)}' "$INPUT" | sort | uniq -c | sort -rn > "$OUT_DIR/${BASENAME}_response_codes.txt"


awk '{
  dt=$4
  gsub("\\[","",dt)
  split(dt, a, ":")
  print a[2]
}' "$INPUT" | sort | uniq -c | sort -k2,2n > "$OUT_DIR/${BASENAME}_hourly_activity.txt"


awk '{
  dt=$4
  gsub("\\[","",dt)
  split(dt, a, ":")
  print a[1]
}' "$INPUT" | sort | uniq -c | sort > "$OUT_DIR/${BASENAME}_daily_activity.txt"


awk '$(NF-1)==404 {
  dt=$4
  gsub("\\[","",dt)
  split(dt, a, ":")
  print a[2]
}' "$INPUT" | sort | uniq -c | sort -rn > "$OUT_DIR/${BASENAME}_404_by_hour.txt"


awk '{counts[$2]=$1}
END{
  max=0
  for (h in counts) if (counts[h] > max) max = counts[h]
  for (i=0; i<24; i++) {
    h=sprintf("%02d", i)
    c=(h in counts)?counts[h]:0
    bar_len=(max>0)?int((50*c)/max):0
    bar=""
    for (j=0; j<bar_len; j++) bar=bar "#"
    printf "%s | %-50s %d\n", h, bar, c
  }
}' "$OUT_DIR/${BASENAME}_hourly_activity.txt" > "$OUT_DIR/${BASENAME}_hourly_chart.txt"

echo "Analysis complete for $INPUT"
echo "Summary: $SUMMARY_FILE"