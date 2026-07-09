#!/bin/bash
# analyze_logs.sh - Read NASA-style access logs and write summary files.
# Usage: ./analyze_logs.sh path/to/log [another.log ...]
#
# Optional: SAMPLE_LINES=50000 ./analyze_logs.sh ...   (only first N lines per file)

set -eu
export LC_ALL=C

HERE="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_DIR="${OUTPUT_DIR:-$HERE/output}"
SAMPLE_LINES="${SAMPLE_LINES:-}"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 logfile.log [more logs...]" >&2
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

# ---------- small helpers ----------

minute_to_dt() {
  awk -v minute="$1" '
    BEGIN {
      split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec", M, " ")
      cb["Jan"]=0; cb["Feb"]=31; cb["Mar"]=59; cb["Apr"]=90
      cb["May"]=120; cb["Jun"]=151; cb["Jul"]=181; cb["Aug"]=212
      cb["Sep"]=243; cb["Oct"]=273; cb["Nov"]=304; cb["Dec"]=334
      md["Jan"]=31; md["Feb"]=28; md["Mar"]=31; md["Apr"]=30
      md["May"]=31; md["Jun"]=30; md["Jul"]=31; md["Aug"]=31
      md["Sep"]=30; md["Oct"]=31; md["Nov"]=30; md["Dec"]=31
      m = minute + 0
      doy = int(m / 1440) + 1
      rem = m % 1440
      hh = int(rem / 60)
      mm = rem % 60
      for (i = 1; i <= 12; i++) {
        mon = M[i]
        first = cb[mon] + 1
        last = cb[mon] + md[mon]
        if (doy >= first && doy <= last) {
          day = doy - cb[mon]
          printf "%02d/%s/1995 %02d:%02d\n", day, mon, hh, mm
          exit
        }
      }
    }
  '
}

compute_outage() {
  awk '
    BEGIN { prev = -1; gmax = -1 }
    {
      cur = $1 + 0
      if (prev < 0) { prev = cur; next }
      gap = cur - prev
      if (gap > gmax) { gmax = gap; gstart = prev; gend = cur }
      prev = cur
    }
    END {
      if (gmax < 0) print "none"
      else print gstart, gend, gmax
    }
  ' "$1" >"$2"
}

build_excluded_days() {
  awk -v gs="$1" -v ge="$2" '
    BEGIN {
      split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec", M, " ")
      cb["Jan"]=0; cb["Feb"]=31; cb["Mar"]=59; cb["Apr"]=90
      cb["May"]=120; cb["Jun"]=151; cb["Jul"]=181; cb["Aug"]=212
      cb["Sep"]=243; cb["Oct"]=273; cb["Nov"]=304; cb["Dec"]=334
      md["Jan"]=31; md["Feb"]=28; md["Mar"]=31; md["Apr"]=30
      md["May"]=31; md["Jun"]=30; md["Jul"]=31; md["Aug"]=31
      md["Sep"]=30; md["Oct"]=31; md["Nov"]=30; md["Dec"]=31
    }
    function dk_from_min(m,    doy, rem, i, mon, first, last, day) {
      doy = int(m / 1440) + 1
      for (i = 1; i <= 12; i++) {
        mon = M[i]
        first = cb[mon] + 1
        last = cb[mon] + md[mon]
        if (doy >= first && doy <= last) {
          day = doy - cb[mon]
          return sprintf("%02d/%s/%d", day, mon, 1995)
        }
      }
      return ""
    }
    BEGIN {
      for (m = gs + 1; m <= ge - 1; m++) {
        d = dk_from_min(m)
        if (d != "") print d
      }
    }
  ' | sort -u >"$3"
}

# ---------- one log file ----------

analyze_one() {
  LOG="$1"
  base=$(basename "$LOG")
  stem=${base%.log}

  md_out="$OUTPUT_DIR/analysis_${stem}.md"
  hours_tsv="$OUTPUT_DIR/${stem}_hours.tsv"
  days_tsv="$OUTPUT_DIR/${stem}_days.tsv"
  hosts_tmp="$OUTPUT_DIR/${stem}_hosts.tsv"
  urls_tmp="$OUTPUT_DIR/${stem}_urls.tsv"
  errh_tmp="$OUTPUT_DIR/${stem}_err_hours.tsv"
  errhost_tmp="$OUTPUT_DIR/${stem}_err_hosts.tsv"
  sorted_minutes="$OUTPUT_DIR/${stem}_minutes_sorted.txt"
  gap_file="$OUTPUT_DIR/${stem}_outage_gap.txt"
  excl_days="$OUTPUT_DIR/${stem}_excluded_days.txt"
  : >"$excl_days"

  if [ ! -f "$LOG" ]; then
    echo "Missing file: $LOG" >&2
    return 1
  fi

  log_src="$LOG"
  if [ -n "$SAMPLE_LINES" ]; then
    log_src="/tmp/sample_${stem}_$$.log"
    head -n "$SAMPLE_LINES" "$LOG" >"$log_src"
  fi

  awk -v HOURS="$hours_tsv" -v DAYS="$days_tsv" \
      -v HOSTS="$hosts_tmp" -v URLS="$urls_tmp" \
      -v ERRH="$errh_tmp" -v ERRHOST="$errhost_tmp" \
      -v OUTDIR="$OUTPUT_DIR" -v STEMFILE="$stem" '
  BEGIN {
    cb["Jan"]=0; cb["Feb"]=31; cb["Mar"]=59; cb["Apr"]=90
    cb["May"]=120; cb["Jun"]=151; cb["Jul"]=181; cb["Aug"]=212
    cb["Sep"]=243; cb["Oct"]=273; cb["Nov"]=304; cb["Dec"]=334
    for (h = 0; h < 24; h++) hourc[h] = 0
  }
  function is_ipv4(h,    n, a, i) {
    n = split(h, a, ".")
    if (n != 4) return 0
    for (i = 1; i <= 4; i++) {
      if (a[i] !~ /^[0-9]{1,3}$/) return 0
      if (a[i] + 0 > 255) return 0
    }
    return 1
  }
  # Only count real HTTP verbs; broken/corrupt lines sometimes put junk in the "method" slot.
  function ok_method(m) {
    return m ~ /^(GET|HEAD|POST|PUT|DELETE|OPTIONS|CONNECT|TRACE|PATCH)$/
  }
  {
    line = $0
    host = $1
    if (match(line, /\[[0-9]{2}\/[A-Za-z]{3}\/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2}/))
      ts = substr(line, RSTART + 1, RLENGTH - 1)
    else { bad++; next }
    split(ts, t1, ":")
    split(t1[1], dmy, "/")
    day = dmy[1] + 0
    mon = dmy[2]
    year = dmy[3] + 0
    hh = t1[2] + 0
    mm = t1[3] + 0
    daykey = sprintf("%02d/%s/%d", day, mon, year)
    if (match(line, /"([^"]*)"/))
      req = substr(line, RSTART + 1, RLENGTH - 2)
    else { bad++; next }
    split(req, rp, " ")
    method = rp[1]
    url = rp[2]
    status = $(NF - 1)
    bytes = $NF
    if (status !~ /^[0-9]{3}$/) { bad++; next }
    total++
    statusc[status]++
    if (ok_method(method)) methodc[method]++
    hourc[hh]++
    dayc[daykey]++
    if (status != 404) {
      host_nf[host]++
      if (url != "") url_nf[url]++
    }
    if (is_ipv4(host)) ipreq++
    else hostnamereq++
    if (bytes ~ /^[0-9]+$/) {
      bsum += bytes + 0
      bcount++
      if (bytes + 0 > bmax) {
        bmax = bytes + 0
        bmaxline = line
      }
    }
    sc = status + 0
    if (sc >= 400) {
      err_hour[hh]++
      err_host[host]++
    }
  }
  END {
    for (h = 0; h < 24; h++) print h "\t" hourc[h] + 0 > HOURS
    close(HOURS)
    for (d in dayc) print dayc[d] "\t" d > DAYS
    close(DAYS)
    for (k in host_nf) print host_nf[k] "\t" k > HOSTS
    close(HOSTS)
    for (k in url_nf) print url_nf[k] "\t" k > URLS
    close(URLS)
    for (k in err_hour) print k "\t" err_hour[k] + 0 > ERRH
    close(ERRH)
    for (k in err_host) print err_host[k] "\t" k > ERRHOST
    close(ERRHOST)
    print total + 0 > (OUTDIR "/" STEMFILE "_totals.txt")
    print bad + 0 > (OUTDIR "/" STEMFILE "_bad.txt")
    print ipreq + 0 > (OUTDIR "/" STEMFILE "_ip.txt")
    print hostnamereq + 0 > (OUTDIR "/" STEMFILE "_hn.txt")
    print bmax + 0 > (OUTDIR "/" STEMFILE "_bmax.txt")
    print bsum + 0 > (OUTDIR "/" STEMFILE "_bsum.txt")
    print bcount + 0 > (OUTDIR "/" STEMFILE "_bcount.txt")
    print bmaxline > (OUTDIR "/" STEMFILE "_bmaxline.txt")
    for (s in statusc) print statusc[s] "\t" s > (OUTDIR "/" STEMFILE "_status.tsv")
    close((OUTDIR "/" STEMFILE "_status.tsv"))
    for (m in methodc) print methodc[m] "\t" m > (OUTDIR "/" STEMFILE "_method.tsv")
    close((OUTDIR "/" STEMFILE "_method.tsv"))
  }
  ' "$log_src"

  total=$(cat "$OUTPUT_DIR/${stem}_totals.txt")
  bad=$(cat "$OUTPUT_DIR/${stem}_bad.txt")
  ipr=$(cat "$OUTPUT_DIR/${stem}_ip.txt")
  hnr=$(cat "$OUTPUT_DIR/${stem}_hn.txt")
  bmax=$(cat "$OUTPUT_DIR/${stem}_bmax.txt")
  bsum=$(cat "$OUTPUT_DIR/${stem}_bsum.txt")
  bcount=$(cat "$OUTPUT_DIR/${stem}_bcount.txt")
  bmaxline=$(cat "$OUTPUT_DIR/${stem}_bmaxline.txt")

  pct_ip="0"
  pct_hn="0"
  denom=$((ipr + hnr))
  if [ "$denom" -gt 0 ]; then
    pct_ip=$(awk -v a="$ipr" -v d="$denom" 'BEGIN { printf "%.2f", 100 * a / d }')
    pct_hn=$(awk -v a="$hnr" -v d="$denom" 'BEGIN { printf "%.2f", 100 * a / d }')
  fi

  err404=$(awk -F '\t' '$2==404 { print $1+0; exit }' "$OUTPUT_DIR/${stem}_status.tsv" || true)
  [ -n "$err404" ] || err404="0"

  top_line=$(sort -rn "$OUTPUT_DIR/${stem}_status.tsv" | head -1)
  top_status_cnt=$(echo "$top_line" | cut -f1)
  top_status=$(echo "$top_line" | cut -f2)
  top_status_pct=$(awk -v c="$top_status_cnt" -v t="$total" 'BEGIN { if (t>0) printf "%.2f", 100*c/t; else print "0" }')

  TAB="$(printf '\t')"
  peak_hour=$(sort -t "$TAB" -k2,2nr "$hours_tsv" | head -1 | cut -f1)
  quiet_line=$(awk -F "$TAB" '$2+0 > 0 { print }' "$hours_tsv" | sort -t "$TAB" -k2,2n | head -1)
  quiet_hour=$(echo "$quiet_line" | cut -f1)
  quiet_hour_cnt=$(echo "$quiet_line" | cut -f2)
  min_line=$(sort -t "$TAB" -k2,2n "$hours_tsv" | head -1)
  min_hour=$(echo "$min_line" | cut -f1)
  min_hour_cnt=$(echo "$min_line" | cut -f2)

  busy_line=$(sort -t "$TAB" -k1,1rn "$days_tsv" | head -1)
  busy_day=$(echo "$busy_line" | cut -f2)
  busy_day_cnt=$(echo "$busy_line" | cut -f1)

  outage_txt="No large gap found between minutes that have at least one request."
  if echo "$stem" | grep -q "Aug95"; then
    awk '
      BEGIN {
        cb["Jan"]=0; cb["Feb"]=31; cb["Mar"]=59; cb["Apr"]=90
        cb["May"]=120; cb["Jun"]=151; cb["Jul"]=181; cb["Aug"]=212
        cb["Sep"]=243; cb["Oct"]=273; cb["Nov"]=304; cb["Dec"]=334
      }
      function lm(day, mon, year, hh, mm,    doy) {
        if (year != 1995) return -1
        if (!(mon in cb)) return -1
        doy = cb[mon] + day
        return (doy - 1) * 1440 + hh * 60 + mm
      }
      {
        if (match($0, /\[[0-9]{2}\/[A-Za-z]{3}\/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2}/)) {
          ts = substr($0, RSTART + 1, RLENGTH - 1)
        } else next
        split(ts, t1, ":")
        split(t1[1], dmy, "/")
        x = lm(dmy[1]+0, dmy[2], dmy[3]+0, t1[2]+0, t1[3]+0)
        if (x >= 0) print x
      }
    ' "$log_src" | sort -n | uniq >"$sorted_minutes"

    compute_outage "$sorted_minutes" "$gap_file"
    read -r gs ge gm <"$gap_file" || true
    if [ -n "$gs" ] && [ "$gs" != "none" ] && [ "$gm" -ge 120 ]; then
      dt_last=$(minute_to_dt "$gs")
      dt_next=$(minute_to_dt "$ge")
      hours_out=$(awk -v g="$gm" 'BEGIN { printf "%.2f", g/60 }')
      outage_txt="Gap between minutes that still have requests: **$dt_last** then **$dt_next** (~${hours_out} hours apart by minute index)."
      if [ "$ge" -gt "$gs" ]; then
        build_excluded_days "$gs" "$ge" "$excl_days"
      fi
    fi

    zline=$(awk '
      {
        if (match($0, /\[[0-9]{2}\/Aug\/1995:/)) {
          split($0, a, "[")
          split(a[2], b, "]")
          split(b[1], t1, ":")
          day = substr(t1[1], 1, 2) + 0
          hh = t1[2] + 0
          hidx = (day - 1) * 24 + hh
          c[hidx]++
        }
      }
      END {
        run = 0; rs = -1; best = 0; bs = -1
        for (h = 0; h < 31 * 24; h++) {
          tot = (h in c) ? c[h] : 0
          if (tot == 0) {
            if (rs < 0) rs = h
            run++
          } else {
            if (run > best) { best = run; bs = rs }
            rs = -1
            run = 0
          }
        }
        if (run > best) { best = run; bs = rs }
        if (best <= 0 || bs < 0) print "none"
        else print bs, bs + best - 1, best
      }
    ' "$log_src")
    zstart=$(echo "$zline" | awk '{ print $1 }')
    zend=$(echo "$zline" | awk '{ print $2 }')
    zlen=$(echo "$zline" | awk '{ print $3 }')
    if [ -n "$zstart" ] && [ "$zstart" != "none" ]; then
      zd1=$((zstart / 24 + 1))
      zh1=$((zstart % 24))
      zd2=$((zend / 24 + 1))
      zh2=$((zend % 24))
      empty_blk=$(printf "Longest stretch with **zero lines** every clock hour: Aug %02d %02d:00 to Aug %02d %02d:59 (%d hours)." \
        "$zd1" "$zh1" "$zd2" "$zh2" "$zlen")
      outage_txt="$outage_txt

$empty_blk"
    fi
  fi

  median_day=$(awk -F '\t' '{ print $1+0 }' "$days_tsv" | sort -n | awk '{ a[NR]=$1 } END { if (NR==0) print 0; else print a[int((NR+1)/2)] }')

  if [ -s "$excl_days" ]; then
    quiet_day=$(awk -F '\t' -v med="$median_day" 'NR==FNR { if (NF) x[$0]=1; next }
      ($1+0) >= med*0.5 && !($2 in x) { print }' "$excl_days" "$days_tsv" | sort -t "$TAB" -k1,1n | head -1 | cut -f2)
    quiet_day_cnt=$(awk -F '\t' -v med="$median_day" 'NR==FNR { if (NF) x[$0]=1; next }
      ($1+0) >= med*0.5 && !($2 in x) { print }' "$excl_days" "$days_tsv" | sort -t "$TAB" -k1,1n | head -1 | cut -f1)
  else
    quiet_day=$(awk -F '\t' -v med="$median_day" '$1+0 >= med*0.5 { print }' "$days_tsv" | sort -t "$TAB" -k1,1n | head -1 | cut -f2)
    quiet_day_cnt=$(awk -F '\t' -v med="$median_day" '$1+0 >= med*0.5 { print }' "$days_tsv" | sort -t "$TAB" -k1,1n | head -1 | cut -f1)
  fi

  avg_bytes=$(awk -v s="$bsum" -v c="$bcount" 'BEGIN { if (c>0) printf "%.2f", s/c; else print "0" }')

  {
    echo "# Analysis: \`$stem\`"
    echo ""
    echo "Source: \`$LOG\`"
    echo ""
    echo "## Parsing"
    echo ""
    echo "- Parsed requests: **$total**"
    echo "- Skipped bad lines: **$bad**"
    echo ""
    echo "## Basic analysis"
    echo ""
    echo "### Top 10 hosts (404 excluded)"
    echo ""
    sort -rn "$hosts_tmp" | awk -v lim=10 -F '\t' 'NF>=2 && ++n<=lim {
      printf "%d. `%s` — %d requests\n", n, $2, $1
    }'
    echo ""
    echo "### IP vs hostname"
    echo ""
    echo "IPv4 requests: **$ipr** (**${pct_ip}%**)."
    echo "Hostname requests: **$hnr** (**${pct_hn}%**)."
    echo ""
    echo "### Top 10 URLs (404 excluded)"
    echo ""
    sort -rn "$urls_tmp" | awk -v lim=10 -F '\t' 'NF>=2 && ++n<=lim {
      printf "%d. `%s` — %d requests\n", n, $2, $1
    }'
    echo ""
    echo "### HTTP methods"
    echo ""
    echo "| Method | Count |"
    echo "| --- | ---: |"
    sort -rn "$OUTPUT_DIR/${stem}_method.tsv" | head -20 | while IFS="$TAB" read -r cnt meth; do
      echo "| $meth | $cnt |"
    done
    echo ""
    echo "### 404 errors"
    echo ""
    echo "**$err404** responses with status 404."
    echo ""
    echo "### Response codes"
    echo ""
    echo "Most common status: **$top_status** ($top_status_cnt hits, ${top_status_pct}% of lines)."
    echo ""
    echo "| Code | Count |"
    echo "| --- | ---: |"
    sort -rn "$OUTPUT_DIR/${stem}_status.tsv" | head -15 | while IFS="$TAB" read -r cnt code; do
      echo "| $code | $cnt |"
    done
    echo ""
    echo "## Time-based analysis"
    echo ""
    echo "### Requests by hour"
    echo ""
    echo "| Hour | Count |"
    echo "| --- | ---: |"
    sort -t "$TAB" -k1,1n "$hours_tsv" | while IFS="$TAB" read -r h c; do
      printf "| %02d | %s |\n" "$h" "$c"
    done
    echo ""
    echo "Peak hour: **$peak_hour**"
    echo "Quietest hour (with traffic): **$quiet_hour** ($quiet_hour_cnt requests)"
    echo "Minimum hour bucket: **$min_hour** ($min_hour_cnt requests)"
    echo ""
    echo "### Busiest day"
    echo ""
    echo "**$busy_day** with **$busy_day_cnt** requests."
    echo ""
    echo "### Quietest normal day"
    echo ""
    echo "Among days with at least half the median daily traffic: **$quiet_day** (**$quiet_day_cnt** requests; median daily **$median_day**)."
    echo ""
    echo "## Advanced"
    echo ""
    echo "### Continuity / gaps (August)"
    echo ""
    echo "$outage_txt"
    echo ""
    echo "### Response sizes"
    echo ""
    echo "- Largest: **$bmax** bytes"
    echo "- Example line: \`$bmaxline\`"
    echo "- Average (numeric bytes only): **$avg_bytes** over $bcount responses"
    echo ""
    echo "### Errors (status >= 400) by hour"
    echo ""
    echo "| Hour | Errors |"
    echo "| --- | ---: |"
    sort -t "$TAB" -k1,1n "$errh_tmp" | while IFS="$TAB" read -r hh cnt; do
      printf "| %02d | %s |\n" "$hh" "$cnt"
    done
    echo ""
    echo "### Top hosts for errors"
    echo ""
    sort -rn "$errhost_tmp" | awk -v lim=10 -F '\t' 'NF>=2 && ++n<=lim {
      printf "%d. `%s` — %d\n", n, $2, $1
    }'
  } >"$md_out"

  if [ -n "$SAMPLE_LINES" ] && [ "$log_src" != "$LOG" ]; then
    rm -f "$log_src"
  fi

  echo "Wrote $md_out"
}

for f in "$@"; do
  analyze_one "$f"
done
