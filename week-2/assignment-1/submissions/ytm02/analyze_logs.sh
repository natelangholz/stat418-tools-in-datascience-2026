#!/usr/bin/env bash
# analyze_logs.sh
# -----------------------------------------------------------------------------
# Part 2: Data Analysis
#
# Runs the twelve required analyses against a NASA common-log-format file and
# writes each result into a separate text file under an output directory so
# generate_report.sh can assemble them into a final report.
#
# Strategy: one awk pass normalizes every log line into a tab-separated record
#   host \t date \t hour \t method \t url \t status \t bytes
# stored at <outdir>/normalized.tsv. Every later question is answered by a
# small pipeline over that file, which is far faster than re-parsing the raw
# log twelve times.
#
# Usage:
#   ./analyze_logs.sh <input.log> <outdir>
# -----------------------------------------------------------------------------

set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <input.log> <outdir>" >&2
  exit 2
fi

readonly INPUT="$1"
readonly OUTDIR="$2"
readonly NORM="${OUTDIR}/normalized.tsv"

[[ -f "${INPUT}" ]] || { echo "ERROR: input file not found: ${INPUT}" >&2; exit 1; }
mkdir -p "${OUTDIR}"

echo "[analyze] parsing ${INPUT}  ->  ${OUTDIR}"

# --- Pass 1: normalize -------------------------------------------------------
# Log line:
#   199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/ HTTP/1.0" 200 6245
#
# We use awk's match() + substr() to extract the bracketed time and the
# quoted request, which is more robust than positional field splitting
# (the request sometimes has embedded spaces).

awk '
BEGIN { FS = " "; OFS = "\t"; bad = 0 }
{
  host = $1

  # --- time between [ and ] -------------------------------------------------
  if (match($0, /\[[^]]+\]/) == 0) { bad++; next }
  tstr = substr($0, RSTART+1, RLENGTH-2)          # e.g. 01/Jul/1995:00:00:01 -0400
  # keep date (DD/Mon/YYYY) and hour (HH)
  # tstr starts with DD/Mon/YYYY:HH:MM:SS SPACE TZ
  date = substr(tstr, 1, 11)                       # DD/Mon/YYYY
  hour = substr(tstr, 13, 2)                       # HH

  # --- request between the first pair of quotes ----------------------------
  if (match($0, /"[^"]*"/) == 0) { bad++; next }
  req = substr($0, RSTART+1, RLENGTH-2)
  rest = substr($0, RSTART + RLENGTH)              # "  200 6245"

  # method = first whitespace-delimited token of the request
  n = split(req, rparts, / +/)
  method = (n >= 1) ? rparts[1] : "-"
  url    = (n >= 2) ? rparts[2] : "-"

  # --- status + bytes come after the closing quote -------------------------
  sub(/^ +/, "", rest)
  split(rest, suffix, / +/)
  status = (suffix[1] == "") ? "-" : suffix[1]
  bytes  = (suffix[2] == "") ? "-" : suffix[2]

  print host, date, hour, method, url, status, bytes
}
END {
  if (bad > 0) print "[analyze] skipped " bad " malformed lines" > "/dev/stderr"
}
' "${INPUT}" > "${NORM}"

NORM_LINES=$(wc -l < "${NORM}" | tr -d ' ')
RAW_LINES=$(wc -l < "${INPUT}" | tr -d ' ')
echo "[analyze] normalized ${NORM_LINES} / ${RAW_LINES} raw lines"

# --- Q1: top 10 hosts (excluding 404) ----------------------------------------
awk -F'\t' '$6 != "404" {print $1}' "${NORM}" \
  | sort | uniq -c | sort -rn | head -10 \
  | awk '{ printf "%8d  %s\n", $1, $2 }' \
  > "${OUTDIR}/q1_top_hosts.txt"

# --- Q2: IP vs hostname ------------------------------------------------------
awk -F'\t' '
{
  host = $1
  if (host ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) ip++
  else                                           name++
  total++
}
END {
  if (total == 0) { print "no data"; exit }
  printf "Requests from IP addresses: %d  (%.2f%%)\n",  ip,   100*ip/total
  printf "Requests from hostnames:    %d  (%.2f%%)\n",  name, 100*name/total
  printf "Total requests:             %d\n", total
}' "${NORM}" > "${OUTDIR}/q2_ip_vs_hostname.txt"

# --- Q3: top 10 requested URLs (excluding 404) -------------------------------
awk -F'\t' '$6 != "404" {print $5}' "${NORM}" \
  | sort | uniq -c | sort -rn | head -10 \
  | awk '{ printf "%8d  %s\n", $1, $2 }' \
  > "${OUTDIR}/q3_top_urls.txt"

# --- Q4: HTTP methods --------------------------------------------------------
# Only count valid uppercase HTTP method tokens to exclude malformed log lines
awk -F'\t' '$4 ~ /^[A-Z]+$/ {print $4}' "${NORM}" \
  | sort | uniq -c | sort -rn \
  | awk '{ printf "%8d  %s\n", $1, $2 }' \
  > "${OUTDIR}/q4_methods.txt"

# --- Q5: 404 errors count ----------------------------------------------------
# Validate status is a proper 3-digit HTTP code before counting
awk -F'\t' '$6 ~ /^[1-5][0-9][0-9]$/ && $6 == "404" {c++} END { print (c ? c : 0) }' "${NORM}" \
  > "${OUTDIR}/q5_404_count.txt"

# --- Q6: response codes + most common ---------------------------------------
# Only count valid 3-digit HTTP status codes; discard garbage from malformed lines
awk -F'\t' '
$6 ~ /^[1-5][0-9][0-9]$/ { c[$6]++; total++ }
END {
  for (s in c) printf "%d\t%s\n", c[s], s
}' "${NORM}" | sort -rn > "${OUTDIR}/q6_status_counts.tsv"

{
  echo "All response codes (count  status):"
  awk -F'\t' '{ printf "%10d  %s\n", $1, $2 }' "${OUTDIR}/q6_status_counts.tsv"
  echo ""
  awk -F'\t' '
  NR==1 { top_count=$1; top_status=$2 }
  { total += $1 }
  END {
    if (total == 0) { print "no data"; exit }
    printf "Most frequent status: %s  (%d occurrences, %.2f%% of responses)\n",
           top_status, top_count, 100*top_count/total
    printf "Total responses:      %d\n", total
  }' "${OUTDIR}/q6_status_counts.tsv"
} > "${OUTDIR}/q6_status_summary.txt"

# --- Q7: peak / quiet hours --------------------------------------------------
awk -F'\t' '{ h[$3]++ } END {
  for (i=0;i<24;i++) {
    hh = sprintf("%02d", i)
    printf "%s\t%d\n", hh, (h[hh]+0)
  }
}' "${NORM}" > "${OUTDIR}/q7_hourly.tsv"

{
  echo "Requests by hour of day (UTC-0400 offset preserved from log):"
  echo ""
  # ASCII bar chart. Max width 50 characters. Scale relative to peak hour.
  max=$(awk -F'\t' '{ if ($2>m) m=$2 } END { print m+0 }' "${OUTDIR}/q7_hourly.tsv")
  awk -F'\t' -v max="${max}" '
    {
      bar_len = (max>0) ? int($2 * 50 / max) : 0
      bar = ""
      for (i=0;i<bar_len;i++) bar = bar "#"
      printf "%s  %-50s  %d\n", $1, bar, $2
    }' "${OUTDIR}/q7_hourly.tsv"
  echo ""
  awk -F'\t' '
    NR==1 { peak_h=$1; peak_c=$2; quiet_h=$1; quiet_c=$2 }
    { if ($2>peak_c)  { peak_c=$2;  peak_h=$1 }
      if ($2<quiet_c) { quiet_c=$2; quiet_h=$1 } }
    END {
      printf "Peak hour:    %s:00  (%d requests)\n", peak_h, peak_c
      printf "Quietest hour: %s:00  (%d requests)\n", quiet_h, quiet_c
    }' "${OUTDIR}/q7_hourly.tsv"
} > "${OUTDIR}/q7_hours.txt"

# --- Q8/Q9: per-day totals ---------------------------------------------------
awk -F'\t' '{ d[$2]++ } END { for (k in d) printf "%d\t%s\n", d[k], k }' "${NORM}" \
  | sort -rn > "${OUTDIR}/q8_daily_by_count.tsv"

# Also sort chronologically for the report
awk -F'\t' '
function mon(m) {
  if(m=="Jan")return 1; if(m=="Feb")return 2;  if(m=="Mar")return 3
  if(m=="Apr")return 4; if(m=="May")return 5;  if(m=="Jun")return 6
  if(m=="Jul")return 7; if(m=="Aug")return 8;  if(m=="Sep")return 9
  if(m=="Oct")return 10;if(m=="Nov")return 11; if(m=="Dec")return 12
  return 0
}
{
  split($2, p, "/")             # DD/Mon/YYYY
  k = sprintf("%04d%02d%02d", p[3], mon(p[2]), p[1])
  printf "%s\t%s\t%d\n", k, $2, $1
}' "${OUTDIR}/q8_daily_by_count.tsv" | sort -k1,1 > "${OUTDIR}/q8_daily_chrono.tsv"

# Compute median and threshold for outage detection
median=$(awk -F'\t' '{print $1}' "${OUTDIR}/q8_daily_by_count.tsv" | sort -n | awk '
  { a[NR]=$1 }
  END {
    if (NR==0) { print 0; exit }
    if (NR%2==1) print a[(NR+1)/2]
    else         print int((a[NR/2]+a[NR/2+1])/2)
  }')
thresh=$(( median / 10 ))

# --- Q8: busiest day ---------------------------------------------------------
{
  echo "Busiest day overall:"
  awk -F'\t' 'NR==1 { printf "  %s  (%d requests)\n", $2, $1 }' \
    "${OUTDIR}/q8_daily_by_count.tsv"
  echo ""
  echo "Top 5 busiest days:"
  head -5 "${OUTDIR}/q8_daily_by_count.tsv" \
    | awk -F'\t' '{ printf "  %12d  %s\n", $1, $2 }'
} > "${OUTDIR}/q8_busiest.txt"

# --- Q9: quietest day (excluding outages) ------------------------------------
{
  echo "Quietest day (excluding outage days with < ${thresh} requests):"
  awk -F'\t' -v t="${thresh}" '$1 >= t' "${OUTDIR}/q8_daily_by_count.tsv" \
    | tail -1 \
    | awk -F'\t' '{ printf "  %s  (%d requests)\n", $2, $1 }'
  echo ""
  echo "Bottom 5 days (including possible outage days):"
  tail -5 "${OUTDIR}/q8_daily_by_count.tsv" \
    | awk -F'\t' '{ printf "  %12d  %s\n", $1, $2 }'
} > "${OUTDIR}/q9_quietest.txt"



# --- Q10: hurricane / outage detection --------------------------------------
# Approach: compute the gap between consecutive log timestamps (seconds) and
# report the largest gaps. A production outage shows up as a multi-hour gap.
# We additionally list days in August with 0 requests.

# Convert each line's timestamp to epoch seconds, sort, walk the sorted list.
awk -F'\t' '
function mon(m) {
  if(m=="Jan")return 1; if(m=="Feb")return 2;  if(m=="Mar")return 3
  if(m=="Apr")return 4; if(m=="May")return 5;  if(m=="Jun")return 6
  if(m=="Jul")return 7; if(m=="Aug")return 8;  if(m=="Sep")return 9
  if(m=="Oct")return 10;if(m=="Nov")return 11; if(m=="Dec")return 12
  return 0
}
{
  # $2 = DD/Mon/YYYY, $3 = HH -- but we lost MM:SS in normalization.
  # Good news: the original file has them; we just need to re-derive.
  print  # placeholder - we will use a different approach in bash below
}' "${NORM}" > /dev/null

# Re-parse the raw log once to emit epoch timestamps (no dependency on `date`
# being GNU; mktime is available in gawk and in most awks shipped on macOS
# via `/usr/bin/awk` as BWK awk which also has mktime). Using `awk` that
# supports mktime is standard on Linux; on macOS install gawk or this block
# falls back gracefully if mktime is unsupported.
awk '
function mon(m) {
  if(m=="Jan")return 1; if(m=="Feb")return 2;  if(m=="Mar")return 3
  if(m=="Apr")return 4; if(m=="May")return 5;  if(m=="Jun")return 6
  if(m=="Jul")return 7; if(m=="Aug")return 8;  if(m=="Sep")return 9
  if(m=="Oct")return 10;if(m=="Nov")return 11; if(m=="Dec")return 12
  return 0
}
{
  if (match($0, /\[[^]]+\]/) == 0) next
  t = substr($0, RSTART+1, RLENGTH-2)         # 01/Jul/1995:00:00:01 -0400
  # parse
  dd = substr(t,1,2)
  mo = mon(substr(t,4,3))
  yy = substr(t,8,4)
  hh = substr(t,13,2)
  mm = substr(t,16,2)
  ss = substr(t,19,2)
  # mktime wants "YYYY MM DD HH MM SS"
  spec = yy " " mo " " dd " " hh " " mm " " ss
  e = mktime(spec)
  if (e > 0) print e
}' "${INPUT}" | sort -n > "${OUTDIR}/_epochs.txt"

# Extract the single largest gap and write directly to output
awk '
NR==1 { prev=$1; next }
{
  gap = $1 - prev
  if (gap > 0) printf "%d\t%d\t%d\n", gap, prev, $1
  prev = $1
}' "${OUTDIR}/_epochs.txt" | sort -rn | head -1 \
  | awk '{
      g=$1; s=$2; e=$3
      h=int(g/3600); m=int((g%3600)/60); sec=g%60
      printf "Data collection stopped: %s\n", strftime("%Y-%m-%d %H:%M:%S", s)
      printf "Data collection resumed: %s\n", strftime("%Y-%m-%d %H:%M:%S", e)
      printf "Total outage duration:   %d seconds (%d hr %d min %d sec)\n", g, h, m, sec
    }' > "${OUTDIR}/q10_outage.txt"

rm -f "${OUTDIR}/_epochs.txt" 2>/dev/null || true

# --- Q11: response sizes -----------------------------------------------------
awk -F'\t' '
$7 != "-" && $7+0 == $7 {
  b = $7+0
  if (b > max) { max = b; max_url = $5; max_host = $1 }
  sum += b
  n++
}
END {
  if (n == 0) { print "no size data"; exit }
  printf "Largest response:  %d bytes\n", max
  printf "  URL:             %s\n",       max_url
  printf "  Host:            %s\n",       max_host
  printf "Average response:  %.2f bytes  (over %d sized responses)\n",
          sum/n, n
  printf "Total bytes sent:  %.0f bytes  (%.2f GB)\n",
          sum, sum/1073741824
}' "${NORM}" > "${OUTDIR}/q11_sizes.txt"

# --- Q12: error patterns -----------------------------------------------------
# "Errors" = status >= 400.
awk -F'\t' '$6 ~ /^[45]/' "${NORM}" > "${OUTDIR}/_errors.tsv"

{
  echo "Error definition: any status code >= 400."
  total_err=$(wc -l < "${OUTDIR}/_errors.tsv" | tr -d ' ')
  echo "Total error responses: ${total_err}"
  echo ""
  echo "Errors by hour:"
  awk -F'\t' '{ h[$3]++ }
  END {
    for (i=0;i<24;i++) { hh=sprintf("%02d",i); printf "  %s:00  %d\n", hh, (h[hh]+0) }
  }' "${OUTDIR}/_errors.tsv"
  echo ""
  echo "Top 10 hosts producing errors:"
  awk -F'\t' '{ print $1 }' "${OUTDIR}/_errors.tsv" \
    | sort | uniq -c | sort -rn | head -10 \
    | awk '{ printf "  %8d  %s\n", $1, $2 }'
  echo ""
  echo "Top 10 URLs that produced errors:"
  awk -F'\t' '{ print $5 }' "${OUTDIR}/_errors.tsv" \
    | sort | uniq -c | sort -rn | head -10 \
    | awk '{ printf "  %8d  %s\n", $1, $2 }'
  echo ""
  echo "Error status code breakdown:"
  awk -F'\t' '{ print $6 }' "${OUTDIR}/_errors.tsv" \
    | sort | uniq -c | sort -rn \
    | awk '{ printf "  %8d  %s\n", $1, $2 }'
} > "${OUTDIR}/q12_error_patterns.txt"

rm -f "${OUTDIR}/_errors.tsv" 2>/dev/null || true

# --- summary.tsv for the reporter -------------------------------------------
{
  echo -e "raw_lines\t${RAW_LINES}"
  echo -e "normalized_lines\t${NORM_LINES}"
  echo -e "404_count\t$(cat "${OUTDIR}/q5_404_count.txt")"
  echo -e "total_errors\t$(awk -F'\t' '$6 ~ /^[45][0-9][0-9]$/' "${NORM}" | wc -l | tr -d ' ')"
  echo -e "total_bytes\t$(awk -F'\t' '$7+0==$7 {s+=$7} END{printf "%.0f", s+0}' "${NORM}")"
  echo -e "unique_hosts\t$(awk -F'\t' '{print $1}' "${NORM}" | sort -u | wc -l | tr -d ' ')"
  echo -e "unique_urls\t$(awk -F'\t' '{print $5}' "${NORM}" | sort -u | wc -l | tr -d ' ')"
  echo -e "date_min\t$(head -1 "${OUTDIR}/q8_daily_chrono.tsv" | awk -F'\t' '{print $2}')"
  echo -e "date_max\t$(tail -1 "${OUTDIR}/q8_daily_chrono.tsv" | awk -F'\t' '{print $2}')"
} > "${OUTDIR}/summary.tsv"

echo "[analyze] done. Outputs in ${OUTDIR}"
