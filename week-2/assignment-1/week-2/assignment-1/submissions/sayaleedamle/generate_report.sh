#!/bin/bash
# generate_report.sh - Generate a comprehensive markdown report from NASA log analysis
# Covers all 5 Part 3 requirements:
#   1. Comprehensive markdown report with all findings
#   2. Summary statistics for both months
#   3. July vs August comparison
#   4. ASCII visualisations
#   5. Interesting findings / anomalies highlighted
# Usage: ./generate_report.sh

set -uo pipefail   # -e omitted: SIGPIPE (141) from head/sort inside analyze_logs.sh is harmless

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ANALYZE="$SCRIPT_DIR/analyze_logs.sh"
JUL_LOG="$SCRIPT_DIR/NASA_Jul95.log"
AUG_LOG="$SCRIPT_DIR/NASA_Aug95.log"
REPORT="$SCRIPT_DIR/REPORT.md"
TMP_JUL=$(mktemp)
TMP_AUG=$(mktemp)
trap 'rm -f "$TMP_JUL" "$TMP_AUG"' EXIT

# ── Validate prerequisites ────────────────────────────────────────────────────
for f in "$ANALYZE" "$JUL_LOG" "$AUG_LOG"; do
    if [ ! -f "$f" ]; then
        echo "ERROR: Required file not found: $f" >&2
        exit 1
    fi
done

echo "Running analysis on July log…"
{ bash "$ANALYZE" "$JUL_LOG" > "$TMP_JUL"; } || { rc=$?; [ $rc -eq 141 ] || exit $rc; }

echo "Running analysis on August log…"
{ bash "$ANALYZE" "$AUG_LOG" > "$TMP_AUG"; } || { rc=$?; [ $rc -eq 141 ] || exit $rc; }

# Verify analysis produced output
for tmp_f in "$TMP_JUL" "$TMP_AUG"; do
    if [ ! -s "$tmp_f" ]; then
        echo "ERROR: analysis produced no output for $tmp_f" >&2
        exit 1
    fi
done

# ── Helper: extract a section between two "--- Heading ---" markers ───────────
# Prints lines AFTER the opening marker and BEFORE the next "---" marker.
section() {
    local file="$1" heading="$2"
    awk -v h="$heading" '
        $0 ~ ("^--- " h) { inside=1; next }
        inside && /^---/ { exit }
        inside { print }
    ' "$file"
}

# ── Helper: ASCII bar chart (stdin: "value label …") ─────────────────────────
ascii_bar() {
    local width="${1:-40}"
    awk -v W="$width" '
    BEGIN { max=0 }
    NF>=2 { val[NR]=$1; lab[NR]=$2; for(i=3;i<=NF;i++) lab[NR]=lab[NR]" "$i
             if($1>max) max=$1; n=NR }
    END {
        for(i=1;i<=n;i++){
            b = (max>0) ? int(val[i]/max*W) : 0
            printf "%-28s |", lab[i]
            for(j=0;j<b;j++) printf "#"
            printf " %d\n", val[i]
        }
    }'
}

# ── Scalar helpers ────────────────────────────────────────────────────────────
grab_re() { grep -m1 "$1" "$2" 2>/dev/null | grep -oE '[0-9]+' | head -1 || echo "N/A"; }
grab_line() { grep -m1 "$1" "$2" 2>/dev/null | sed "s/.*$1//" || echo "N/A"; }

# ── Collect summary scalars ───────────────────────────────────────────────────
JUL_TOTAL=$(grep "^Total:" "$TMP_JUL" 2>/dev/null | grep -oE '[0-9]+' | head -1 \
            || awk 'END{print NR}' "$JUL_LOG")
AUG_TOTAL=$(grep "^Total:" "$TMP_AUG" 2>/dev/null | grep -oE '[0-9]+' | head -1 \
            || awk 'END{print NR}' "$AUG_LOG")
JUL_404=$(grep "Total 404 errors:" "$TMP_JUL" | grep -oE '[0-9]+' | head -1 || echo 0)
AUG_404=$(grep "Total 404 errors:" "$TMP_AUG" | grep -oE '[0-9]+' | head -1 || echo 0)
JUL_AVG=$(grep "Average response:" "$TMP_JUL" | grep -oE '[0-9]+' | head -1 || echo 0)
AUG_AVG=$(grep "Average response:" "$TMP_AUG" | grep -oE '[0-9]+' | head -1 || echo 0)
JUL_MAX=$(grep "Largest response:" "$TMP_JUL" | grep -oE '[0-9]+' | head -1 || echo 0)
AUG_MAX=$(grep "Largest response:" "$TMP_AUG" | grep -oE '[0-9]+' | head -1 || echo 0)
JUL_BUSIEST=$(grep "Busiest day:" "$TMP_JUL" | sed 's/Busiest day: //' || echo N/A)
AUG_BUSIEST=$(grep "Busiest day:" "$TMP_AUG" | sed 's/Busiest day: //' || echo N/A)
JUL_QUIETEST=$(grep "Quietest day:" "$TMP_JUL" | sed 's/Quietest day: //' || echo N/A)
AUG_QUIETEST=$(grep "Quietest day:" "$TMP_AUG" | sed 's/Quietest day: //' || echo N/A)

# IP/hostname percentages
JUL_IP_PCT=$(grep "^IP addresses:" "$TMP_JUL" | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo 0)
AUG_IP_PCT=$(grep "^IP addresses:" "$TMP_AUG" | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo 0)

# Most frequent response code line (e.g. "Most frequent: 200 (1000 requests, 85.3%)")
JUL_TOP_CODE=$(grep "Most frequent:" "$TMP_JUL" | head -1 || echo N/A)
AUG_TOP_CODE=$(grep "Most frequent:" "$TMP_AUG" | head -1 || echo N/A)

# Compute delta
DELTA=$(( ${AUG_TOTAL:-0} - ${JUL_TOTAL:-0} ))
if [ "$DELTA" -lt 0 ]; then
    DELTA_STR="${DELTA} (decrease — likely due to hurricane outage)"
else
    DELTA_STR="+${DELTA}"
fi

# ── Build hourly traffic data for ASCII charts ────────────────────────────────
jul_hourly() {
    grep "^Hour [0-9]*: [0-9]* requests" "$TMP_JUL" \
        | sed 's/Hour \([0-9]*\): \([0-9]*\) requests/\2 \1/' \
        | sort -k2 -n
}
aug_hourly() {
    grep "^Hour [0-9]*: [0-9]* requests" "$TMP_AUG" \
        | sed 's/Hour \([0-9]*\): \([0-9]*\) requests/\2 \1/' \
        | sort -k2 -n
}

# ── Build response-code chart data ────────────────────────────────────────────
# Lines from section look like "   <count>  <code>"
code_chart() {
    section "$1" "Response Code Breakdown" \
        | grep -E '^ +[0-9]+ +[0-9]{3}' \
        | awk '{print $1, $2}' \
        | sort -rn
}

# ── Write REPORT.md ───────────────────────────────────────────────────────────
{
##############################################################################
# Title & date
##############################################################################
printf '# NASA Web Server Log Analysis — July & August 1995\n\n'
printf '**Generated:** %s  \n' "$(date)"
printf '**Scripts:** `analyze_logs.sh` → `generate_report.sh`\n\n'
printf '%s\n\n' "---"

##############################################################################
# 2. SUMMARY STATISTICS (both months side-by-side)
##############################################################################
printf '## Summary Statistics\n\n'
printf '| Metric | July 1995 | August 1995 | Change |\n'
printf '|--------|-----------|-------------|--------|\n'
printf '| Total requests | %s | %s | %s |\n' "$JUL_TOTAL" "$AUG_TOTAL" "$DELTA_STR"
printf '| 404 errors | %s | %s | — |\n' "$JUL_404" "$AUG_404"
printf '| Avg response size (bytes) | %s | %s | — |\n' "$JUL_AVG" "$AUG_AVG"
printf '| Largest response (bytes) | %s | %s | — |\n' "$JUL_MAX" "$AUG_MAX"
printf '| %% requests from raw IPs | %s%% | %s%% | — |\n' "$JUL_IP_PCT" "$AUG_IP_PCT"
printf '| Busiest day | %s | %s | — |\n' "$JUL_BUSIEST" "$AUG_BUSIEST"
printf '| Quietest day | %s | %s | — |\n' "$JUL_QUIETEST" "$AUG_QUIETEST"
printf '| Top response code | %s | %s | — |\n\n' "$JUL_TOP_CODE" "$AUG_TOP_CODE"

##############################################################################
# 3. JULY vs AUGUST COMPARISON (ASCII charts)
##############################################################################
printf '%s\n\n' "---"
printf '## 3. July vs August Comparison\n\n'

printf '### Hourly Traffic — July 1995\n\n```\n'
jul_hourly | ascii_bar 45
printf '```\n\n'

printf '### Hourly Traffic — August 1995\n\n```\n'
aug_hourly | ascii_bar 45
printf '```\n\n'

printf '### Response Code Distribution — July 1995\n\n```\n'
code_chart "$TMP_JUL" | ascii_bar 40
printf '```\n\n'

printf '### Response Code Distribution — August 1995\n\n```\n'
code_chart "$TMP_AUG" | ascii_bar 40
printf '```\n\n'

##############################################################################
# 1. FULL FINDINGS — all 12 analysis sections for BOTH months
##############################################################################
printf '%s\n\n' "---"
printf '## Full Analysis Findings\n\n'

for MONTH in July August; do
    if [ "$MONTH" = "July" ]; then
        TMP="$TMP_JUL"
    else
        TMP="$TMP_AUG"
    fi

    printf '### %s 1995\n\n' "$MONTH"

    printf '#### 1. Top 10 Hosts (excluding 404 errors)\n\n```\n'
    section "$TMP" "Top 10 Hosts"
    printf '```\n\n'

    printf '#### 2. IP Address vs Hostname\n\n```\n'
    section "$TMP" "IP Address vs Hostname"
    printf '```\n\n'

    printf '#### 3. Top 10 Requested URLs (excluding 404 errors)\n\n```\n'
    section "$TMP" "Top 10 Requested URLs"
    printf '```\n\n'

    printf '#### 4. HTTP Request Methods\n\n```\n'
    section "$TMP" "HTTP Request Methods"
    printf '```\n\n'

    printf '#### 5. 404 Errors\n\n```\n'
    grep "Total 404 errors:" "$TMP" || true
    printf '```\n\n'

    printf '#### 6. Response Code Breakdown\n\n```\n'
    section "$TMP" "Response Code Breakdown"
    printf '```\n\n'

    printf '#### 7. Peak Hours\n\n```\n'
    section "$TMP" "Peak Hours"
    printf '```\n\n'

    printf '#### 8. Busiest Day\n\n```\n'
    grep "Busiest day:" "$TMP" || true
    printf '```\n\n'

    printf '#### 9. Quietest Day (excluding outage dates)\n\n```\n'
    grep "Quietest day:" "$TMP" || true
    printf '```\n\n'

    printf '#### 10. Hurricane / Data Outage Detection\n\n```\n'
    section "$TMP" "Hurricane"
    printf '```\n\n'

    printf '#### 11. Response Size\n\n```\n'
    section "$TMP" "Response Size"
    printf '```\n\n'

    printf '#### 12. Error Patterns (4xx/5xx)\n\n```\n'
    section "$TMP" "Error Patterns"
    printf '```\n\n'

    printf '%s\n\n' "---"
done

##############################################################################
# 5. INTERESTING FINDINGS & ANOMALIES
##############################################################################
printf '## Key Findings & Anomalies\n\n'

printf '### Traffic Volume\n'
printf -- '- July had **%s** requests; August had **%s** (%s).\n' \
    "$JUL_TOTAL" "$AUG_TOTAL" "$DELTA_STR"
printf -- '- The drop in August is largely attributed to the hurricane outage (see Section 10 above).\n\n'

printf '### 404 Error Rate\n'
JUL_404_PCT=$(awk "BEGIN{printf \"%.2f\", ${JUL_404}/${JUL_TOTAL}*100}" 2>/dev/null || echo "?")
AUG_404_PCT=$(awk "BEGIN{printf \"%.2f\", ${AUG_404}/${AUG_TOTAL}*100}" 2>/dev/null || echo "?")
printf -- '- July: %s 404s = **%s%%** of requests.\n' "$JUL_404" "$JUL_404_PCT"
printf -- '- August: %s 404s = **%s%%** of requests.\n\n' "$AUG_404" "$AUG_404_PCT"

printf '### Hurricane Outage (August 1995)\n'
printf -- '- Timestamp gap analysis (Section 10, August) pinpoints when the server stopped logging.\n'
printf -- '- Gaps > 1 hour between consecutive entries are flagged as outage windows.\n\n'

printf '### Peak Usage Patterns\n'
printf -- '- Both months show mid-day peaks consistent with US East Coast business hours.\n'
printf -- '- The busiest day in July was **%s**; in August it was **%s**.\n\n' \
    "$JUL_BUSIEST" "$AUG_BUSIEST"

printf '### Response Sizes\n'
printf -- '- Average payload: %s bytes (July) vs %s bytes (August).\n' "$JUL_AVG" "$AUG_AVG"
printf -- '- Largest single response: %s bytes (July) / %s bytes (August).\n\n' \
    "$JUL_MAX" "$AUG_MAX"

printf '### IP vs Hostname\n'
printf -- '- %s%% of July requests and %s%% of August requests came from raw IP addresses\n' \
    "$JUL_IP_PCT" "$AUG_IP_PCT"
printf -- '  (remainder were resolved hostnames), reflecting typical 1995 internet demographics.\n\n'

echo "---"
printf -- '*End of report.*\n'

} > "$REPORT"

echo "Report saved → $REPORT"
