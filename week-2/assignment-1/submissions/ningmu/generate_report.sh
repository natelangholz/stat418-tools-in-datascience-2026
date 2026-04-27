#!/bin/bash
# generate_report.sh - Build a markdown report from the NASA log analyses.
# Usage: ./generate_report.sh [JUL_LOG] [AUG_LOG] [OUTPUT_FILE]
#
# Defaults:
#   JUL_LOG     = data/NASA_Jul95.log
#   AUG_LOG     = data/NASA_Aug95.log
#   OUTPUT_FILE = REPORT.md

# Note: `pipefail` is intentionally omitted because several pipelines
# use `| head -N`, which causes upstream tools to exit 141 (SIGPIPE).
set -eu

JUL_LOG="${1:-data/NASA_Jul95.log}"
AUG_LOG="${2:-data/NASA_Aug95.log}"
OUTFILE="${3:-REPORT.md}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ANALYZE="$SCRIPT_DIR/analyze_logs.sh"

if [[ ! -x "$ANALYZE" ]]; then
  echo "Error: analyze_logs.sh not found or not executable." >&2
  exit 1
fi

for f in "$JUL_LOG" "$AUG_LOG"; do
  if [[ ! -f "$f" ]]; then
    echo "Error: log file missing: $f" >&2
    echo "Run ./download_data.sh first." >&2
    exit 1
  fi
done

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

JUL_OUT="$TMPDIR/jul.txt"
AUG_OUT="$TMPDIR/aug.txt"

echo "[report] Running analysis on $JUL_LOG ..."
"$ANALYZE" "$JUL_LOG" > "$JUL_OUT"

echo "[report] Running analysis on $AUG_LOG ..."
"$ANALYZE" "$AUG_LOG" > "$AUG_OUT"

# Helper: extract one numbered section from an analyze_logs output.
# Stops at the next "## " header or the trailing "====" banner.
extract_section () {
  local file="$1"
  local header="$2"
  awk -v h="$header" '
    $0 ~ "^## " h {flag=1; next}
    flag && (/^## / || /^====/ || /^Analysis complete/) {flag=0}
    flag {print}
  ' "$file"
}

jul_total=$(grep '^Total log lines' "$JUL_OUT" | awk '{print $4}')
aug_total=$(grep '^Total log lines' "$AUG_OUT" | awk '{print $4}')

jul_404=$(extract_section "$JUL_OUT" "5[.]" \
  | grep -oE 'errors:[[:space:]]*[0-9]+' | awk '{print $2}')
aug_404=$(extract_section "$AUG_OUT" "5[.]" \
  | grep -oE 'errors:[[:space:]]*[0-9]+' | awk '{print $2}')

echo "[report] Writing $OUTFILE ..."

{
cat <<EOF
# NASA Web Server Log Analysis Report

**Author:** Christine (ningmu)
**Generated:** $(date '+%Y-%m-%d %H:%M:%S')
**Data sources:**
- \`$JUL_LOG\`
- \`$AUG_LOG\`

---

## Executive Summary

This report analyses NASA Kennedy Space Center web server access logs from
**July 1995** and **August 1995**. The August data contains a noticeable
gap caused by **Hurricane Erin**, which knocked the NASA KSC network
offline for several days.

| Metric          | July 1995    | August 1995  |
|-----------------|--------------|--------------|
| Total requests  | ${jul_total} | ${aug_total} |
| 404 errors      | ${jul_404}   | ${aug_404}   |

---

## July 1995 - Detailed Findings

### 1. Top 10 hosts (excluding 404s)
\`\`\`
$(extract_section "$JUL_OUT" "1[.]")
\`\`\`

### 2. IP addresses vs hostnames
\`\`\`
$(extract_section "$JUL_OUT" "2[.]")
\`\`\`

### 3. Top 10 most-requested URLs (excluding 404s)
\`\`\`
$(extract_section "$JUL_OUT" "3[.]")
\`\`\`

### 4. HTTP methods
\`\`\`
$(extract_section "$JUL_OUT" "4[.]")
\`\`\`

### 5. 404 errors
\`\`\`
$(extract_section "$JUL_OUT" "5[.]")
\`\`\`

### 6. Response code distribution
\`\`\`
$(extract_section "$JUL_OUT" "6[.]")
\`\`\`

### 7. Activity by hour of day
\`\`\`
$(extract_section "$JUL_OUT" "7[.]")
\`\`\`

### 8. Busiest day
\`\`\`
$(extract_section "$JUL_OUT" "8[.]")
\`\`\`

### 9. Quietest day
\`\`\`
$(extract_section "$JUL_OUT" "9[.]")
\`\`\`

### 10. Outage detection
\`\`\`
$(extract_section "$JUL_OUT" "10[.]")
\`\`\`

### 11. Response size
\`\`\`
$(extract_section "$JUL_OUT" "11[.]")
\`\`\`

### 12. Error patterns
\`\`\`
$(extract_section "$JUL_OUT" "12[.]")
\`\`\`

---

## August 1995 - Detailed Findings

### 1. Top 10 hosts (excluding 404s)
\`\`\`
$(extract_section "$AUG_OUT" "1[.]")
\`\`\`

### 2. IP addresses vs hostnames
\`\`\`
$(extract_section "$AUG_OUT" "2[.]")
\`\`\`

### 3. Top 10 most-requested URLs (excluding 404s)
\`\`\`
$(extract_section "$AUG_OUT" "3[.]")
\`\`\`

### 4. HTTP methods
\`\`\`
$(extract_section "$AUG_OUT" "4[.]")
\`\`\`

### 5. 404 errors
\`\`\`
$(extract_section "$AUG_OUT" "5[.]")
\`\`\`

### 6. Response code distribution
\`\`\`
$(extract_section "$AUG_OUT" "6[.]")
\`\`\`

### 7. Activity by hour of day
\`\`\`
$(extract_section "$AUG_OUT" "7[.]")
\`\`\`

### 8. Busiest day
\`\`\`
$(extract_section "$AUG_OUT" "8[.]")
\`\`\`

### 9. Quietest day
\`\`\`
$(extract_section "$AUG_OUT" "9[.]")
\`\`\`

### 10. Outage detection (Hurricane Erin)
\`\`\`
$(extract_section "$AUG_OUT" "10[.]")
\`\`\`

### 11. Response size
\`\`\`
$(extract_section "$AUG_OUT" "11[.]")
\`\`\`

### 12. Error patterns
\`\`\`
$(extract_section "$AUG_OUT" "12[.]")
\`\`\`

---

## July vs August Comparison

| Metric          | July         | August       |
|-----------------|--------------|--------------|
| Total requests  | ${jul_total} | ${aug_total} |
| 404 errors      | ${jul_404}   | ${aug_404}   |

### ASCII Visualization: Activity Comparison
\`\`\`
EOF

# Helper: draw a horizontal bar (40 chars wide) for comparison charts.
# Uses Unicode full block / light shade for a cleaner look.
BAR_FULL=$(printf '\u2588')   # U+2588 FULL BLOCK
BAR_EMPTY=$(printf '\u2591')  # U+2591 LIGHT SHADE

draw_bar () {
  awk -v lbl="$1" -v val="$2" -v max="$3" \
      -v full="$BAR_FULL" -v empty="$BAR_EMPTY" 'BEGIN {
    w = 40
    filled = int((val / max) * w + 0.5)
    if (filled > w) filled = w
    bar = ""
    for (i = 0; i < filled; i++) bar = bar full
    for (i = filled; i < w; i++) bar = bar empty
    printf "%-9s %s  %d\n", lbl ":", bar, val
  }'
}

echo "Monthly Request Volume:"
echo
draw_bar "July"   "$jul_total" 2000000
draw_bar "August" "$aug_total" 2000000
echo "          |---------|---------|---------|---------|"
echo "          0        500k     1000k    1500k    2000k"
echo
echo "404 Error Comparison:"
echo
draw_bar "July"   "$jul_404" 20000
draw_bar "August" "$aug_404" 20000
echo "          |---------|---------|---------|---------|"
echo "          0         5k       10k      15k      20k"

cat <<EOF
\`\`\`

### ASCII chart - daily request volume (detail)

**July 1995:**
\`\`\`
EOF

awk '$4 ~ /^\[/ {d=substr($4,2); split(d,a,":"); print a[1]}' "$JUL_LOG" \
  | sort | uniq -c \
  | awk -v full="$BAR_FULL" '{
      counts[NR]=$1; days[NR]=$2;
      if ($1>max) max=$1
    }
    END {
      for (i=1; i<=NR; i++) {
        n = int(counts[i] / max * 60)
        bar = ""
        for (j=0; j<n; j++) bar = bar full
        printf "%-12s %8d %s\n", days[i], counts[i], bar
      }
    }'

echo '```'
echo
echo '**August 1995:**'
echo '```'

awk '$4 ~ /^\[/ {d=substr($4,2); split(d,a,":"); print a[1]}' "$AUG_LOG" \
  | sort | uniq -c \
  | awk -v full="$BAR_FULL" '{
      counts[NR]=$1; days[NR]=$2;
      if ($1>max) max=$1
    }
    END {
      for (i=1; i<=NR; i++) {
        n = int(counts[i] / max * 60)
        bar = ""
        for (j=0; j<n; j++) bar = bar full
        printf "%-12s %8d %s\n", days[i], counts[i], bar
      }
    }'

cat <<EOF
\`\`\`

---

## July vs August - Headline Comparisons

- **August had fewer total requests than July** (${aug_total} vs
  ${jul_total}), largely because of the Hurricane Erin outage: an
  entire day of log data (02/Aug/1995) is missing, plus partial
  coverage on 01/Aug and 03/Aug.
- **Despite lower August volume, the 404 error rate was slightly
  higher** than in July (see section 5 of each month). So the drop in
  traffic was not matched by a proportional drop in bad requests.
- The busiest single day shifted from mid-July (**13/Jul/1995**) to
  the last day of August (**31/Aug/1995**), which is consistent with
  traffic ramping back up after the outage.

---

## Interesting Findings & Anomalies

- **Hurricane Erin outage.** See section 10 for August - the largest gap
  in log timestamps identifies the outage window and its duration.
- **GIF-heavy traffic.** The most-requested URLs in both months are small
  GIF images (NASA/KSC logos, countdown clock, etc.). This reflects the
  pre-CDN era: every HTML page pulled several tiny images.
- **Most requests are successful.** Code 200 dominates, typically
  accompanied by 304 (Not Modified) responses - a sign of active
  client-side caching.
- **GET is essentially the only method used**, which matches a read-only
  public documentation / mission site.
- **Daytime peak (US east coast).** Activity rises sharply during US
  daytime hours and is quietest in the early-morning hours (UTC-0400).

---

## Caveats

- Some log rows are malformed (binary garbage in the request field, or
  missing spaces). My analyses filter these out where possible
  (e.g. \`\$4 ~ /^\[/\` for timestamps, \`\$9 ~ /^[1-5][0-9][0-9]\$/\`
  for status codes, and \`\$6 ~ /^[A-Z]+\$/\` for HTTP methods).
- **Response-code distribution may contain rare three-digit values**
  (e.g. 234, 363, 527, 543) that are not real HTTP status codes.
  Some malformed log entries appear to shift fields, so unusual
  three-digit values may reflect parsing noise rather than valid HTTP
  status codes. The figures for the common codes (200, 304, 302, 404,
  403, 500) are unaffected.

EOF
} > "$OUTFILE"

echo "[report] Done. Wrote $OUTFILE"
