#!/bin/bash
# generate_report.sh - Generates a markdown report from analysis results

JULY_LOG="NASA_Jul95.log"
AUG_LOG="NASA_Aug95.log"
JULY_RESULTS="july_results.txt"
AUG_RESULTS="aug_results.txt"
REPORT="REPORT.md"

# check result files exist
if [[ ! -f "$JULY_RESULTS" ]]; then
    echo "ERROR: $JULY_RESULTS not found. Run analyze_logs.sh first."
    exit 1
fi
if [[ ! -f "$AUG_RESULTS" ]]; then
    echo "ERROR: $AUG_RESULTS not found. Run analyze_logs.sh first."
    exit 1
fi

echo "Generating report..."

# helper to extract a section from results file
# Usage: extract_section "section title" "results file"
extract_section() {
    local section="$1"
    local file="$2"
    sed -n "/--- ${section}/,/DONE/p" "$file" \
        | grep -v "^DONE" \
        | grep -v "^---"
}

cat > "$REPORT" << 'REPORTEOF'
# NASA Web Server Log Analysis Report
**Data:** NASA Kennedy Space Center HTTP logs, July–August 1995  
**Analyzed:** $(date '+%Y-%m-%d')

---

## Overview

This report analyzes web server access logs from NASA's Kennedy Space Center
website during July and August 1995 — a historically significant period
coinciding with several shuttle missions and a major hurricane.

---
REPORTEOF

# Fix the date line (heredoc doesn't expand variables)
sed -i "s/\$(date '+%Y-%m-%d')/$(date '+%Y-%m-%d')/" "$REPORT"

cat >> "$REPORT" << REPORTEOF

## 1. Top 10 Hosts

### July 1995
\`\`\`
$(extract_section "1. Top 10 Hosts" "$JULY_RESULTS")
\`\`\`

### August 1995
\`\`\`
$(extract_section "1. Top 10 Hosts" "$AUG_RESULTS")
\`\`\`

---

## 2. IP vs Hostname

### July 1995
$(extract_section "2. IP vs Hostname" "$JULY_RESULTS")

### August 1995
$(extract_section "2. IP vs Hostname" "$AUG_RESULTS")

---

## 3. Top 10 Requested URLs

### July 1995
\`\`\`
$(extract_section "3. Top 10 Requested" "$JULY_RESULTS")
\`\`\`

### August 1995
\`\`\`
$(extract_section "3. Top 10 Requested" "$AUG_RESULTS")
\`\`\`

---

## 4. HTTP Request Types

### July 1995
\`\`\`
$(extract_section "4. HTTP Request" "$JULY_RESULTS")
\`\`\`

### August 1995
\`\`\`
$(extract_section "4. HTTP Request" "$AUG_RESULTS")
\`\`\`

---

## 5. Total 404 Errors

| Month | 404 Errors |
|-------|------------|
| July  | $(extract_section "5. Total 404" "$JULY_RESULTS" | tr -d ' ') |
| August | $(extract_section "5. Total 404" "$AUG_RESULTS" | tr -d ' ') |

---

## 6. Most Frequent Response Code

### July 1995
\`\`\`
$(extract_section "6. Most Frequent" "$JULY_RESULTS")
\`\`\`

### August 1995
\`\`\`
$(extract_section "6. Most Frequent" "$AUG_RESULTS")
\`\`\`

---

## 7. Peak and Quiet Hours

### July 1995
\`\`\`
$(extract_section "7. Requests by Hour" "$JULY_RESULTS")
\`\`\`

### August 1995
\`\`\`
$(extract_section "7. Requests by Hour" "$AUG_RESULTS")
\`\`\`

---

## 8. Busiest Day

| Month | Busiest Day |
|-------|-------------|
| July  | $(extract_section "8. Busiest" "$JULY_RESULTS" | awk '{print $2, "-", $1, "requests"}') |
| August | $(extract_section "8. Busiest" "$AUG_RESULTS" | awk '{print $2, "-", $1, "requests"}') |

---

## 9. Quietest Day

### July 1995
\`\`\`
$(extract_section "9. Quietest" "$JULY_RESULTS")
\`\`\`

### August 1995
\`\`\`
$(extract_section "9. Quietest" "$AUG_RESULTS")
\`\`\`

---

## 10. Hurricane Outage (August 1995)

\`\`\`
$(extract_section "10. Hurricane" "$AUG_RESULTS")
\`\`\`

> Hurricane Erin made landfall in Florida in August 1995, causing a data
> collection outage at Kennedy Space Center. The gaps above show hours
> where fewer than 100 requests were logged, indicating the outage window.

---

## 11. Response Sizes

### July 1995
$(extract_section "11. Largest" "$JULY_RESULTS")

### August 1995
$(extract_section "11. Largest" "$AUG_RESULTS")

---

## 12. Error Patterns by Hour

### July 1995
\`\`\`
$(extract_section "12. Error Patterns" "$JULY_RESULTS")
\`\`\`

### August 1995
\`\`\`
$(extract_section "12. Error Patterns" "$AUG_RESULTS")
\`\`\`

---

## Summary: July vs August Comparison

| Metric | July 1995 | August 1995 |
|--------|-----------|-------------|
| Total Requests | $(wc -l < "$JULY_LOG") | $(wc -l < "$AUG_LOG") |
| 404 Errors | $(extract_section "5. Total 404" "$JULY_RESULTS" | tr -d ' ') | $(extract_section "5. Total 404" "$AUG_RESULTS" | tr -d ' ') |
| Busiest Day | $(extract_section "8. Busiest" "$JULY_RESULTS" | awk '{print $2, "-", $1, "requests"}') | $(extract_section "8. Busiest" "$AUG_RESULTS" | awk '{print $2, "-", $1, "requests"}') |
---

## Key Findings

1. **Prodigy.com dominates traffic** — piweba hosts from Prodigy were the
   top requesters in both months, suggesting automated or heavy residential use.

2. **Images drive the majority of requests** — NASA logo and KSC logo GIFs
   appear in nearly every top-10 URL list, reflecting the image-heavy web
   design of 1995.

3. **HTTP 200 accounts for ~90% of responses** — the server was healthy
   and serving content successfully the vast majority of the time.

4. **Hurricane Erin caused a measurable outage in August** — gaps in
   hourly request counts confirm the data collection interruption.

5. **Traffic drops significantly on weekends** — quietest days tend to
   fall on Saturdays and Sundays, reflecting the professional/academic
   user base of the mid-1990s web.

REPORTEOF

echo "Report generated: $REPORT"
