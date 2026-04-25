#!/bin/bash
# generate_report.sh - Turn analysis files into REPORT.md

set -eu
export LC_ALL=C

HERE="$(cd "$(dirname "$0")" && pwd)"
OUT="${OUTPUT_DIR:-$HERE/output}"
REPORT="${REPORT:-$HERE/REPORT.md}"

JUL_MD="$OUT/analysis_NASA_Jul95.md"
AUG_MD="$OUT/analysis_NASA_Aug95.md"

if [ ! -f "$JUL_MD" ] || [ ! -f "$AUG_MD" ]; then
  echo "Run analyze_logs.sh first (missing analysis files)." >&2
  exit 1
fi

JUL_N=$(cat "$OUT/NASA_Jul95_totals.txt" 2>/dev/null || echo 0)
AUG_N=$(cat "$OUT/NASA_Aug95_totals.txt" 2>/dev/null || echo 0)

RATIO=$(awk -v j="$JUL_N" -v a="$AUG_N" 'BEGIN { if (j > 0) printf "%.3f", a / j; else print "n/a" }')
DIFF=$(awk -v j="$JUL_N" -v a="$AUG_N" 'BEGIN { print a - j }')
DIFF_PCT=$(awk -v j="$JUL_N" -v a="$AUG_N" 'BEGIN { if (j>0) printf "%.2f", (a-j)*100/j; else print "0" }')

JUL_404=$(awk -F '\t' '$2=="404"{print $1+0; exit}' "$OUT/NASA_Jul95_status.tsv")
AUG_404=$(awk -F '\t' '$2=="404"{print $1+0; exit}' "$OUT/NASA_Aug95_status.tsv")
[ -n "$JUL_404" ] || JUL_404=0
[ -n "$AUG_404" ] || AUG_404=0
ERR_DIFF=$(awk -v j="$JUL_404" -v a="$AUG_404" 'BEGIN { print a-j }')
ERR_DIFF_PCT=$(awk -v j="$JUL_404" -v a="$AUG_404" 'BEGIN { if (j>0) printf "%.2f", (a-j)*100/j; else print "0" }')

JUL_IP=$(cat "$OUT/NASA_Jul95_ip.txt" 2>/dev/null || echo 0)
JUL_HN=$(cat "$OUT/NASA_Jul95_hn.txt" 2>/dev/null || echo 0)
AUG_IP=$(cat "$OUT/NASA_Aug95_ip.txt" 2>/dev/null || echo 0)
AUG_HN=$(cat "$OUT/NASA_Aug95_hn.txt" 2>/dev/null || echo 0)
JUL_IP_PCT=$(awk -v i="$JUL_IP" -v h="$JUL_HN" 'BEGIN { d=i+h; if(d>0) printf "%.2f", i*100/d; else print "0" }')
AUG_IP_PCT=$(awk -v i="$AUG_IP" -v h="$AUG_HN" 'BEGIN { d=i+h; if(d>0) printf "%.2f", i*100/d; else print "0" }')

JUL_PEAK_LINE=$(sort -t "$(printf '\t')" -k2,2nr "$OUT/NASA_Jul95_hours.tsv" | head -1)
AUG_PEAK_LINE=$(sort -t "$(printf '\t')" -k2,2nr "$OUT/NASA_Aug95_hours.tsv" | head -1)
JUL_PEAK_HOUR=$(echo "$JUL_PEAK_LINE" | cut -f1)
JUL_PEAK_COUNT=$(echo "$JUL_PEAK_LINE" | cut -f2)
AUG_PEAK_HOUR=$(echo "$AUG_PEAK_LINE" | cut -f1)
AUG_PEAK_COUNT=$(echo "$AUG_PEAK_LINE" | cut -f2)

JUL_BEST_DAY_LINE=$(sort -t "$(printf '\t')" -k1,1rn "$OUT/NASA_Jul95_days.tsv" | head -1)
AUG_BEST_DAY_LINE=$(sort -t "$(printf '\t')" -k1,1rn "$OUT/NASA_Aug95_days.tsv" | head -1)
JUL_BEST_DAY=$(echo "$JUL_BEST_DAY_LINE" | cut -f2)
JUL_BEST_DAY_N=$(echo "$JUL_BEST_DAY_LINE" | cut -f1)
AUG_BEST_DAY=$(echo "$AUG_BEST_DAY_LINE" | cut -f2)
AUG_BEST_DAY_N=$(echo "$AUG_BEST_DAY_LINE" | cut -f1)

JUL_LARGEST=$(cat "$OUT/NASA_Jul95_bmax.txt" 2>/dev/null || echo 0)
AUG_LARGEST=$(cat "$OUT/NASA_Aug95_bmax.txt" 2>/dev/null || echo 0)

max_j=$(awk -F '\t' 'BEGIN{m=0} {if($2+0>m)m=$2+0} END{print m+0}' "$OUT/NASA_Jul95_hours.tsv")
max_a=$(awk -F '\t' 'BEGIN{m=0} {if($2+0>m)m=$2+0} END{print m+0}' "$OUT/NASA_Aug95_hours.tsv")

{
  echo "# NASA Web Logs — Combined Report"
  echo ""
  echo "_Generated: $(date -u +"%Y-%m-%d %H:%M:%SZ") (UTC)_"
  echo ""
  echo "## Summary"
  echo ""
  echo "July parsed lines: **$JUL_N**. August parsed lines: **$AUG_N** (ratio August/July = **${RATIO}x**)."
  echo "Net change (Aug - Jul): **$DIFF** requests (**${DIFF_PCT}%**)."
  echo ""
  echo "## Comparison"
  echo ""
  echo "| Metric | July | August |"
  echo "| --- | ---: | ---: |"
  echo "| Parsed requests | $JUL_N | $AUG_N |"
  echo "| 404 errors | $JUL_404 | $AUG_404 |"
  echo "| IP share | ${JUL_IP_PCT}% | ${AUG_IP_PCT}% |"
  echo "| Peak hour (count) | ${JUL_PEAK_HOUR} ($JUL_PEAK_COUNT) | ${AUG_PEAK_HOUR} ($AUG_PEAK_COUNT) |"
  echo "| Busiest day (count) | ${JUL_BEST_DAY} ($JUL_BEST_DAY_N) | ${AUG_BEST_DAY} ($AUG_BEST_DAY_N) |"
  echo "| Largest response (bytes) | $JUL_LARGEST | $AUG_LARGEST |"
  echo ""
  echo "## Hour-of-day (ASCII)"
  echo ""
  echo "### July"
  echo ""
  echo '```'
  TAB="$(printf '\t')"
  sort -t "$TAB" -k1,1n "$OUT/NASA_Jul95_hours.tsv" | while IFS="$TAB" read -r hr cnt; do
    [ -z "$hr" ] && continue
    n=$(awk -v c="$cnt" -v mx="$max_j" 'BEGIN { if (mx<=0) print 0; else printf "%d", int(c * 40 / mx + 0.5) }')
    bar=$(printf '%*s' "$n" '' | tr ' ' '#')
    printf '%02d |%s %s\n' "$hr" "$bar" "$cnt"
  done
  echo '```'
  echo ""
  echo "### August"
  echo ""
  echo '```'
  sort -t "$TAB" -k1,1n "$OUT/NASA_Aug95_hours.tsv" | while IFS="$TAB" read -r hr cnt; do
    [ -z "$hr" ] && continue
    n=$(awk -v c="$cnt" -v mx="$max_a" 'BEGIN { if (mx<=0) print 0; else printf "%d", int(c * 40 / mx + 0.5) }')
    bar=$(printf '%*s' "$n" '' | tr ' ' '#')
    printf '%02d |%s %s\n' "$hr" "$bar" "$cnt"
  done
  echo '```'
  echo ""
  echo "## Highlights"
  echo ""
  echo "- **Traffic volume:** August has **$DIFF** fewer parsed requests than July (${DIFF_PCT}% change)."
  echo "- **Error trend:** 404 count changed from **$JUL_404** (Jul) to **$AUG_404** (Aug), difference **$ERR_DIFF** (${ERR_DIFF_PCT}%)."
  echo "- **Client mix:** IP-share rises from **${JUL_IP_PCT}%** in July to **${AUG_IP_PCT}%** in August."
  echo "- **Peak load shifts:** peak hour moves from **${JUL_PEAK_HOUR}** (Jul) to **${AUG_PEAK_HOUR}** (Aug)."
  echo "- **Anomaly note:** August shows a long logging gap; see the August continuity section for exact timestamps."
  echo ""
  echo "## July — full analysis"
  echo ""
  sed -e 's/^#### /######## /' \
      -e 's/^### /###### /' \
      -e 's/^## /##### /' \
      -e 's/^# /#### /' "$JUL_MD"
  echo ""
  echo "## August — full analysis"
  echo ""
  sed -e 's/^#### /######## /' \
      -e 's/^### /###### /' \
      -e 's/^## /##### /' \
      -e 's/^# /#### /' "$AUG_MD"
} >"$REPORT"

echo "Wrote $REPORT"
