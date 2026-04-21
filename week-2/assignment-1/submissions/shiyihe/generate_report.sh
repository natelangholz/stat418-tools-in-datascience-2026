#!/bin/bash

jul_file="results/NASA_Jul95_summary.txt"
aug_file="results/NASA_Aug95_summary.txt"
report="REPORT.md"

bar() {
    value=$1
    scale=$2
    n=$((value / scale))
    if [ "$n" -lt 1 ]; then
        n=1
    fi
    printf '%*s' "$n" '' | tr ' ' '#'
}

jul_total=$(wc -l < data/NASA_Jul95.log | xargs)
aug_total=$(wc -l < data/NASA_Aug95.log | xargs)

jul_404=$(grep -A1 "^404 errors:" "$jul_file" | tail -1 | xargs)
aug_404=$(grep -A1 "^404 errors:" "$aug_file" | tail -1 | xargs)

jul_peak=$(grep -A1 "^Peak hour:" "$jul_file" | tail -1 | xargs)
aug_peak=$(grep -A1 "^Peak hour:" "$aug_file" | tail -1 | xargs)

jul_busiest=$(grep -A1 "^Busiest day:" "$jul_file" | tail -1 | xargs)
aug_busiest=$(grep -A1 "^Busiest day:" "$aug_file" | tail -1 | xargs)

jul_quiet=$(grep -A1 "^Quietest day excluding outage dates:" "$jul_file" | tail -1 | xargs)
aug_quiet=$(grep -A1 "^Quietest day excluding outage dates:" "$aug_file" | tail -1 | xargs)

jul_code=$(grep -A1 "^Most frequent response code:" "$jul_file" | tail -1 | xargs)
aug_code=$(grep -A1 "^Most frequent response code:" "$aug_file" | tail -1 | xargs)

jul_largest=$(grep -A2 "^Response size:" "$jul_file" | sed -n '2p' | xargs)
jul_avg=$(grep -A2 "^Response size:" "$jul_file" | sed -n '3p' | xargs)

aug_largest=$(grep -A2 "^Response size:" "$aug_file" | sed -n '2p' | xargs)
aug_avg=$(grep -A2 "^Response size:" "$aug_file" | sed -n '3p' | xargs)

aug_outage_gap=$(grep -A2 "^Hurricane outage:" "$aug_file" | sed -n '2p' | xargs)
aug_outage_duration=$(grep -A2 "^Hurricane outage:" "$aug_file" | sed -n '3p' | xargs)

jul_avg_num=$(grep -A2 "^Response size:" "$jul_file" | sed -n '3p' | awk '{print $2}')
aug_avg_num=$(grep -A2 "^Response size:" "$aug_file" | sed -n '3p' | awk '{print $2}')

higher_traffic=$(awk -v j="$jul_total" -v a="$aug_total" 'BEGIN {if (j > a) print "July"; else print "August"}')
higher_avg=$(awk -v j="$jul_avg_num" -v a="$aug_avg_num" 'BEGIN {if (j > a) print "July"; else print "August"}')

cat > "$report" <<EOF
# NASA Web Server Log Analysis Report

Generated on: $(date)

## Overview

This report summarizes the NASA web server logs from July and August 1995.

## Summary comparison

| Metric | July | August |
|---|---:|---:|
| Total requests | $jul_total | $aug_total |
| 404 errors | $jul_404 | $aug_404 |
| Most frequent response code | $jul_code | $aug_code |
| Peak hour | $jul_peak | $aug_peak |
| Busiest day | $jul_busiest | $aug_busiest |
| Quietest day | $jul_quiet | $aug_quiet |
| Largest response size | $jul_largest | $aug_largest |
| Average response size | $jul_avg | $aug_avg |

## Simple ASCII charts

### Total requests

- July:   $jul_total $(bar "$jul_total" 50000)
- August: $aug_total $(bar "$aug_total" 50000)

### 404 errors

- July:   $jul_404 $(bar "$jul_404" 300)
- August: $aug_404 $(bar "$aug_404" 300)

## Key findings

- $higher_traffic had more total requests.
- The most frequent response code in both months was 200.
- $higher_avg had the larger average response size.
- August had a major outage.
- $aug_outage_gap
- $aug_outage_duration

## July details

\`\`\`
$(cat "$jul_file")
\`\`\`

## August details

\`\`\`
$(cat "$aug_file")
\`\`\`
EOF

echo "REPORT.md generated"
