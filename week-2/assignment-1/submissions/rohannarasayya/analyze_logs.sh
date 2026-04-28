#!/bin/bash
# analyze_logs.sh - Analyze NASA web server access logs
# Usage: ./analyze_logs.sh <logfile>

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <logfile>" >&2
    exit 1
fi

LOGFILE="$1"

if [[ ! -f "$LOGFILE" ]]; then
    echo "Error: File '$LOGFILE' not found." >&2
    exit 1
fi

echo "============================================================"
echo "NASA Web Server Log Analysis"
echo "File: $LOGFILE"
echo "Lines: $(wc -l < "$LOGFILE")"
echo "============================================================"

# ---------------------------------------------------------------------------
# Q1: Top 10 hosts excluding 404 responses
# ---------------------------------------------------------------------------
echo ""
echo "--- Q1: Top 10 Hosts (excluding 404 errors) ---"
awk 'NF >= 10 && $9 != 404 { print $1 }' "$LOGFILE" \
    | sort | uniq -c | sort -rn | head -10 \
    | awk '{ printf "  %8d  %s\n", $1, $2 }' || true

# ---------------------------------------------------------------------------
# Q2: % requests from IPs vs hostnames
# ---------------------------------------------------------------------------
echo ""
echo "--- Q2: IP vs Hostname Requests ---"
awk 'NF >= 10 {
    if ($1 ~ /^[0-9]/) ip++
    else host++
    total++
}
END {
    if (total == 0) { print "  No data"; exit }
    printf "  IP addresses : %d (%.1f%%)\n", ip+0,   (ip+0)/total*100
    printf "  Hostnames    : %d (%.1f%%)\n", host+0, (host+0)/total*100
    printf "  Total        : %d\n", total
}' "$LOGFILE"

# ---------------------------------------------------------------------------
# Q3: Top 10 URLs excluding 404 responses
# ---------------------------------------------------------------------------
echo ""
echo "--- Q3: Top 10 URLs (excluding 404 errors) ---"
awk 'NF >= 10 && $9 != 404 { print $7 }' "$LOGFILE" \
    | sort | uniq -c | sort -rn | head -10 \
    | awk '{ printf "  %8d  %s\n", $1, $2 }' || true

# ---------------------------------------------------------------------------
# Q4: HTTP method counts
# ---------------------------------------------------------------------------
echo ""
echo "--- Q4: HTTP Method Counts ---"
awk 'NF >= 10 { gsub(/"/, "", $6); print $6 }' "$LOGFILE" \
    | sort | uniq -c | sort -rn \
    | awk '{ printf "  %8d  %s\n", $1, $2 }'

# ---------------------------------------------------------------------------
# Q5: Total 404 count
# ---------------------------------------------------------------------------
echo ""
echo "--- Q5: Total 404 Errors ---"
awk 'NF >= 10 && $9 == 404 { count++ }
     END { printf "  404 errors: %d\n", count+0 }' "$LOGFILE"

# ---------------------------------------------------------------------------
# Q6: Most frequent response code and its percentage
# ---------------------------------------------------------------------------
echo ""
echo "--- Q6: Response Code Distribution ---"
awk 'NF >= 10 && $9 ~ /^[0-9]+$/ { codes[$9]++; total++ }
END {
    if (total == 0) { print "  No data"; exit }
    max = 0; top = ""
    for (c in codes) if (codes[c] > max) { max = codes[c]; top = c }
    printf "  Most frequent: HTTP %s  (%d requests, %.1f%%)\n", top, max, max/total*100
}' "$LOGFILE"
echo "  All codes:"
awk 'NF >= 10 && $9 ~ /^[0-9]+$/ { codes[$9]++; total++ }
END {
    for (c in codes)
        printf "    HTTP %s : %7d  (%.1f%%)\n", c, codes[c], codes[c]/total*100
}' "$LOGFILE" | sort

# ---------------------------------------------------------------------------
# Q7: Request count by hour
# ---------------------------------------------------------------------------
echo ""
echo "--- Q7: Requests by Hour of Day ---"
awk 'NF >= 10 {
    # $4 = [01/Jul/1995:14:32:01  => chars 14-15 (1-based) are the hour
    hour = substr($4, 14, 2)
    counts[sprintf("%02d", hour+0)]++
}
END {
    for (h = 0; h <= 23; h++)
        printf "  %02d:00  %d\n", h, counts[sprintf("%02d", h)]+0
}' "$LOGFILE"

# ---------------------------------------------------------------------------
# Q8: Busiest date
# ---------------------------------------------------------------------------
echo ""
echo "--- Q8: Busiest Date ---"
awk 'NF >= 10 {
    # $4 = [01/Jul/1995:...  => chars 2-12 (1-based) are the date
    date = substr($4, 2, 11)
    counts[date]++
}
END {
    max = 0; top = ""
    for (d in counts) if (counts[d] > max) { max = counts[d]; top = d }
    printf "  %s : %d requests\n", top, max
}' "$LOGFILE"

# ---------------------------------------------------------------------------
# Q9: Quietest date excluding outage/gap dates
# Outage dates = days whose count is <= 5% of the mean daily count
# ---------------------------------------------------------------------------
echo ""
echo "--- Q9: Quietest Date (excluding outage/gap dates) ---"
awk 'NF >= 10 { counts[substr($4, 2, 11)]++ }
END {
    n = 0; total = 0
    for (d in counts) { total += counts[d]; n++ }
    if (n == 0) { print "  No data"; exit }
    threshold = (total / n) * 0.05

    min = -1; quiet = ""
    for (d in counts) {
        if (counts[d] <= threshold) continue
        if (min == -1 || counts[d] < min) { min = counts[d]; quiet = d }
    }
    if (quiet == "") print "  (all dates classified as outage)"
    else printf "  %s : %d requests\n", quiet, min
}' "$LOGFILE"

# ---------------------------------------------------------------------------
# Q10: Hurricane outage — detect missing days (complete gaps) and report
#       exact outage start/end timestamps with duration
# ---------------------------------------------------------------------------
echo ""
echo "--- Q10: Hurricane Outage Detection ---"

# Phase 1: show daily counts and detect gap boundaries.
# The awk emits normal display lines plus two sentinel lines:
#   GAP_BEFORE:<DD/Mon/YYYY>  — last day with data before the gap
#   GAP_AFTER:<DD/Mon/YYYY>   — first day with data after the gap
# The while-read loop prints display lines and captures the sentinels.
GAP_BEFORE=""
GAP_AFTER=""

while IFS= read -r line; do
    case "$line" in
        GAP_BEFORE:*) GAP_BEFORE="${line#GAP_BEFORE:}" ;;
        GAP_AFTER:*)  GAP_AFTER="${line#GAP_AFTER:}"  ;;
        *)            echo "$line" ;;
    esac
done < <(awk 'NF >= 10 {
    date = substr($4, 2, 11)
    split(date, p, "/")
    mon_map["Jan"]=1; mon_map["Feb"]=2; mon_map["Mar"]=3
    mon_map["Apr"]=4; mon_map["May"]=5; mon_map["Jun"]=6
    mon_map["Jul"]=7; mon_map["Aug"]=8; mon_map["Sep"]=9
    mon_map["Oct"]=10;mon_map["Nov"]=11;mon_map["Dec"]=12
    key = sprintf("%s-%02d-%02d", p[3], mon_map[p[2]], p[1]+0)
    counts[key]++
    labels[key] = date
}
END {
    if (length(counts) == 0) { print "  No data"; exit }

    n = 0
    for (k in counts) keys[n++] = k
    for (a = 0; a < n-1; a++)
        for (b = a+1; b < n; b++)
            if (keys[a] > keys[b]) { tmp=keys[a]; keys[a]=keys[b]; keys[b]=tmp }

    total = 0
    for (i = 0; i < n; i++) total += counts[keys[i]]
    avg = total / n
    threshold = avg * 0.05

    print "  Full daily counts:"
    for (i = 0; i < n; i++) {
        flag = ""
        if (counts[keys[i]] <= threshold) flag = "  <-- LOW (possible outage)"
        printf "    %s : %6d%s\n", labels[keys[i]], counts[keys[i]], flag
    }

    print ""
    print "  Missing days in date range (complete data gaps):"
    found_gap = 0
    for (i = 0; i < n-1; i++) {
        split(keys[i],   pa, "-")
        split(keys[i+1], pb, "-")
        ep_a = mktime(pa[1] " " (pa[2]+0) " " (pa[3]+0) " 0 0 0")
        ep_b = mktime(pb[1] " " (pb[2]+0) " " (pb[3]+0) " 0 0 0")
        diff_days = int((ep_b - ep_a) / 86400)
        if (diff_days > 1) {
            for (gap = 1; gap < diff_days; gap++) {
                gep = ep_a + gap * 86400
                printf "    MISSING: %s\n", strftime("%d/%b/%Y", gep)
                found_gap++
            }
            printf "GAP_BEFORE:%s\n", labels[keys[i]]
            printf "GAP_AFTER:%s\n",  labels[keys[i+1]]
        }
    }
    if (!found_gap) print "    (none — no fully missing days detected)"
    else printf "  (%d fully missing day(s) = hurricane outage)\n", found_gap
}' "$LOGFILE")

# Phase 2: extract exact boundary timestamps and calculate duration.
# $4 = [DD/Mon/YYYY:HH:MM:SS  $5 = -0400]
if [[ -n "$GAP_BEFORE" && -n "$GAP_AFTER" ]]; then
    START_TS=$(grep "$GAP_BEFORE" "$LOGFILE" | tail -1 \
        | awk '{ts=substr($4,2); tz=$5; gsub(/\]/,"",tz); print ts " " tz}')
    END_TS=$(grep -m 1 "$GAP_AFTER" "$LOGFILE" \
        | awk '{ts=substr($4,2); tz=$5; gsub(/\]/,"",tz); print ts " " tz}')

    echo ""
    awk -v start="$START_TS" -v finish="$END_TS" '
    BEGIN {
        mon_map["Jan"]=1; mon_map["Feb"]=2; mon_map["Mar"]=3
        mon_map["Apr"]=4; mon_map["May"]=5; mon_map["Jun"]=6
        mon_map["Jul"]=7; mon_map["Aug"]=8; mon_map["Sep"]=9
        mon_map["Oct"]=10; mon_map["Nov"]=11; mon_map["Dec"]=12

        # split "DD/Mon/YYYY:HH:MM:SS -0400" on /, :, and space
        split(start,  s, "[/: ]+")
        split(finish, e, "[/: ]+")
        # s[1]=DD s[2]=Mon s[3]=YYYY s[4]=HH s[5]=MM s[6]=SS

        t_start = mktime(s[3] " " mon_map[s[2]] " " (s[1]+0) " " s[4] " " s[5] " " s[6])
        t_end   = mktime(e[3] " " mon_map[e[2]] " " (e[1]+0) " " e[4] " " e[5] " " e[6])

        diff    = t_end - t_start
        hours   = int(diff / 3600)
        minutes = int((diff % 3600) / 60)

        printf "  Outage start : %s\n", start
        printf "  Outage end   : %s\n", finish
        printf "  Duration     : %d hours %d minutes\n", hours, minutes
    }'
fi

# ---------------------------------------------------------------------------
# Q11: Largest and average response bytes (skip "-")
# ---------------------------------------------------------------------------
echo ""
echo "--- Q11: Response Size Statistics ---"
awk 'NF >= 10 && $10 != "-" {
    b = $10 + 0
    if (b > max) max = b
    total += b
    count++
}
END {
    if (count == 0) { print "  No byte data found"; exit }
    printf "  Largest response  : %d bytes  (%.1f KB)\n", max, max/1024
    printf "  Average response  : %.0f bytes  (%.1f KB)\n", total/count, total/count/1024
    printf "  Requests with size: %d\n", count
}' "$LOGFILE"

# ---------------------------------------------------------------------------
# Q12: Error patterns by hour and host (4xx / 5xx)
# ---------------------------------------------------------------------------
echo ""
echo "--- Q12: Error Patterns (4xx/5xx) ---"

echo "  Errors by hour:"
awk 'NF >= 10 && ($9 ~ /^[45]/) {
    hour = substr($4, 14, 2)
    counts[hour]++
    total++
}
END {
    if (total == 0) { print "    (none)"; exit }
    printf "    Total 4xx/5xx errors: %d\n", total
    for (h = 0; h <= 23; h++) {
        hh = sprintf("%02d", h)
        if (counts[hh]+0 > 0)
            printf "    %s:00  %d\n", hh, counts[hh]
    }
}' "$LOGFILE"

echo ""
echo "  Top 10 error-generating hosts:"
awk 'NF >= 10 && ($9 ~ /^[45]/) { print $1 }' "$LOGFILE" \
    | sort | uniq -c | sort -rn | head -10 \
    | awk '{ printf "    %8d  %s\n", $1, $2 }' || true

echo ""
echo "============================================================"
echo "Analysis complete."
echo "============================================================"
