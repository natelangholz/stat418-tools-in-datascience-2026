# permission: chmod +x generate_report.sh
# to run: bash generate_report.sh

#!/bin/bash
set -euo pipefail
export LC_ALL=C

INPUT="analysis_results.txt"
OUTPUT="REPORT.md"

if [ ! -f "$INPUT" ]; then
    printf "Error: %s not found.\n" "$INPUT" >&2
    exit 1
fi

# Split blocks cleanly - use '|| true' to prevent crash if a block is missing
JUL_BLOCK=$(sed -n '/Processing NASA_Jul95.log/,/Processing NASA_Aug95.log/p' "$INPUT" || true)
AUG_BLOCK=$(sed -n '/Processing NASA_Aug95.log/,$p' "$INPUT" || true)

printf "Generating Report...\n"

{
    echo "# NASA Web Server Analysis Report"
    echo "## Global Traffic Analysis: July - August 1995"
    echo ""
    echo "---"

    echo "## 1. Monthly Summary Comparison"
    echo "| Metric | July 1995 | August 1995 |"
    echo "| :--- | :--- | :--- |"
    echo "| **Busiest Day (Date)** | $(echo "$JUL_BLOCK" | grep -A 1 "8. Busiest Day" | tail -n 1 | awk '{print $2}' || echo "N/A") | $(echo "$AUG_BLOCK" | grep -A 1 "8. Busiest Day" | tail -n 1 | awk '{print $2}' || echo "N/A") |"
    echo "| **Quietest Day (Date)** | $(echo "$JUL_BLOCK" | grep -A 1 "9. Quietest Day" | tail -n 1 | awk '{print $2}' || echo "N/A") | $(echo "$AUG_BLOCK" | grep -A 1 "9. Quietest Day" | tail -n 1 | awk '{print $2}' || echo "N/A") |"
    echo "| **Total 404 Errors** | $(echo "$JUL_BLOCK" | grep -A 1 "5. Total 404 Errors" | tail -n 1 | awk '{print $1}' || echo "0") | $(echo "$AUG_BLOCK" | grep -A 1 "5. Total 404 Errors" | tail -n 1 | awk '{print $1}' || echo "0") |"
    echo ""

    echo "## 2. Protocol & Request Methods"
    echo "| Method | July Frequency | August Frequency |"
    echo "| :--- | :--- | :--- |"
    echo "| **GET** | $(echo "$JUL_BLOCK" | grep "GET" | head -n 1 | awk '{print $1}' || echo "0") | $(echo "$AUG_BLOCK" | grep "GET" | head -n 1 | awk '{print $1}' || echo "0") |"
    echo "| **HEAD** | $(echo "$JUL_BLOCK" | grep "HEAD" | awk '{print $1}' || echo "0") | $(echo "$AUG_BLOCK" | grep "HEAD" | awk '{print $1}' || echo "0") |"
    echo "| **POST** | $(echo "$JUL_BLOCK" | grep "POST" | awk '{print $1}' || echo "0") | $(echo "$AUG_BLOCK" | grep "POST" | awk '{print $1}' || echo "0") |"
    echo ""

    echo "## 3. Server Response Success Rates"
    echo "| Status Code | July Success % | August Success % |"
    echo "| :--- | :--- | :--- |"
    echo "| **Code 200 (OK)** | $(echo "$JUL_BLOCK" | grep "Code 200" | awk '{print $3}' | tr -d '()' || echo "0%") | $(echo "$AUG_BLOCK" | grep "Code 200" | awk '{print $3}' | tr -d '()' || echo "0%") |"
    echo ""

    echo "## 4. Host Resolution Metrics"
    echo "| Category | July Percentage | August Percentage |"
    echo "| :--- | :--- | :--- |"
    echo "| **Resolved Hostnames** | $(echo "$JUL_BLOCK" | grep "Hostnames:" | awk '{print $5}' || echo "0%") | $(echo "$AUG_BLOCK" | grep "Hostnames:" | awk '{print $5}' || echo "0%") |"
    echo "| **Raw IP Addresses** | $(echo "$JUL_BLOCK" | grep "IPs:" | awk '{print $2}' || echo "0%") | $(echo "$AUG_BLOCK" | grep "IPs:" | awk '{print $2}' || echo "0%") |"
    echo ""

    echo "## 5. Daily Traffic Volume (Visualized)"
    echo "Comparison of Peak Daily Volume (1 '#' = 5,000 requests)"
    echo "\`\`\`text"
    J_VOL=$(echo "$JUL_BLOCK" | grep -A 1 "8. Busiest Day" | tail -n 1 | awk '{print $1}' || echo "0")
    A_VOL=$(echo "$AUG_BLOCK" | grep -A 1 "8. Busiest Day" | tail -n 1 | awk '{print $1}' || echo "0")
    J_BAR=$([ "$J_VOL" -ge 5000 ] && printf '%.0s#' $(seq 1 $((J_VOL / 5000))) || echo "")
    A_BAR=$([ "$A_VOL" -ge 5000 ] && printf '%.0s#' $(seq 1 $((A_VOL / 5000))) || echo "")
    printf "July Peak   [%-30s] %'d\n" "$J_BAR" "$J_VOL"
    printf "August Peak [%-30s] %'d\n" "$A_BAR" "$A_VOL"
    echo "\`\`\`"

    echo "## 6. Time-Based Analysis: Hourly Peaks"
    echo "| Month | Peak Traffic Hour | Quietest Traffic Hour |"
    echo "| :--- | :--- | :--- |"
    echo "| **July** | $(echo "$JUL_BLOCK" | grep "Peak:" | awk '{print $2, $3, $4}' | tr -d '()' || echo "N/A") | $(echo "$JUL_BLOCK" | grep "Quiet:" | awk '{print $2, $3, $4}' | tr -d '()' || echo "N/A") |"
    echo "| **August** | $(echo "$AUG_BLOCK" | grep "Peak:" | awk '{print $2, $3, $4}' | tr -d '()' || echo "N/A") | $(echo "$AUG_BLOCK" | grep "Quiet:" | awk '{print $2, $3, $4}' | tr -d '()'|| echo "N/A") |"
    echo ""

    echo "## 7. Data Payload Statistics"
    echo "| Metric | July 1995 | August 1995 |"
    echo "| :--- | :--- | :--- |"
    echo "| **Maximum Single Response** | $(echo "$JUL_BLOCK" | grep "Max:" | awk '{print $2, $3}' || echo "0 bytes") | $(echo "$AUG_BLOCK" | grep "Max:" | awk '{print $2, $3}' || echo "0 bytes") |"
    echo "| **Average Response Size** | $(echo "$JUL_BLOCK" | grep "Avg:" | awk '{print $5, $6}' || echo "0 bytes") | $(echo "$AUG_BLOCK" | grep "Avg:" | awk '{print $5, $6}' || echo "0 bytes") |"
    echo ""

    echo "## 8. Top 10 Host Activity (Frequency)"
    echo "| Rank | July Active Host (Hits) | August Active Host (Hits) |"
    echo "| :--- | :--- | :--- |"
    for i in {1..10}; do
        # Use awk to swap columns: $1 is the count, $2 is the host name
        J_H=$(echo "$JUL_BLOCK" | grep -A 11 "1. Top 10 Hosts" | sed -n "$((i+1))p" | awk '{$1=$1; if(NF>=2) print $2 " (" $1 ")"; else if(NF==1) print $1; else print "N/A"}' || echo "N/A")
        A_H=$(echo "$AUG_BLOCK" | grep -A 11 "1. Top 10 Hosts" | sed -n "$((i+1))p" | awk '{$1=$1; if(NF>=2) print $2 " (" $1 ")"; else if(NF==1) print $1; else print "N/A"}' || echo "N/A")
        echo "| $i | ${J_H:-N/A} | ${A_H:-N/A} |"
    done
    echo ""

    echo "## 9. Top 10 Content Requests"
    echo "| Rank | July URL (Hits) | August URL (Hits) |"
    echo "| :--- | :--- | :--- |"
    for i in {1..10}; do
        J_U=$(echo "$JUL_BLOCK" | grep -A 11 "3. Top 10 Requests" | sed -n "$((i+1))p" | awk '{$1=$1; print}' || echo "")
        A_U=$(echo "$AUG_BLOCK" | grep -A 11 "3. Top 10 Requests" | sed -n "$((i+1))p" | awk '{$1=$1; print}' || echo "")
        # Formatted output to handle empty hits
        J_FMT=$(echo "$J_U" | awk '{print $2 " (" $1 ")"}')
        A_FMT=$(echo "$A_U" | awk '{print $2 " (" $1 ")"}')
        echo "| $i | ${J_FMT:-N/A} | ${A_FMT:-N/A} |"
    done
    echo ""

    echo "## 10. Advanced Error Patterns"
    echo "### 10.1 Peak Error Hours"
    echo "| Rank | July Error Hour (Count) | August Error Hour (Count) |"
    echo "| :--- | :--- | :--- |"
    for i in {1..3}; do
        J_ET=$(echo "$JUL_BLOCK" | grep -A 4 "Top 3 Hours for Errors" | sed -n "$((i+1))p" | sed 's/^[ \t]*//' || echo "N/A")
        A_ET=$(echo "$AUG_BLOCK" | grep -A 4 "Top 3 Hours for Errors" | sed -n "$((i+1))p" | sed 's/^[ \t]*//' || echo "N/A")
        echo "| $i | ${J_ET:-N/A} | ${A_ET:-N/A} |"
    done
    echo ""

    echo "### 10.2 Highest Error-Producing Hosts"
    echo "| Rank | July Host (Count) | August Host (Count) |"
    echo "| :--- | :--- | :--- |"
    for i in {1..3}; do
        J_EH=$(echo "$JUL_BLOCK" | grep -A 4 "Top 3 Hosts producing Errors" | sed -n "$((i+1))p" | sed 's/^[ \t]*//' || echo "N/A")
        A_EH=$(echo "$AUG_BLOCK" | grep -A 4 "Top 3 Hosts producing Errors" | sed -n "$((i+1))p" | sed 's/^[ \t]*//' || echo "N/A")
        echo "| $i | ${J_EH:-N/A} | ${A_EH:-N/A} |"
    done
    echo ""

    echo "## 11. Hurricane Outage Analysis"
    echo "> [!CAUTION]"
    echo "> Operational Gap Detected: August 1, 1995 - August 3, 1995"
    echo ""
    echo "| Metric | Data Point |"
    echo "| :--- | :--- |"
    H_STOP=$(echo "$AUG_BLOCK" | grep "Data collection stopped" | sed 's/.*: //' || echo "N/A")
    H_START=$(echo "$AUG_BLOCK" | grep "Data collection resumed" | sed 's/.*: //' || echo "N/A")
    H_DUR=$(echo "$AUG_BLOCK" | grep "Duration:" | awk -F': ' '{print $2}' || echo "N/A")
    echo "| **Outage Start** | ${H_STOP} |"
    echo "| **Outage End** | ${H_START} |"
    echo "| **Total Downtime** | ${H_DUR} |"
    echo ""

    echo "## 12. Technical Spreadsheet Export (CSV)"
    echo "\`\`\`csv"
    echo "Month,GET,HEAD,POST,Busiest_Day_Vol,Max_Bytes,404_Errors"

    # July CSV Extraction
    J_GET=$(echo "$JUL_BLOCK" | grep "GET" | head -n 1 | awk '{print $1}' || echo "0")
    J_HEAD=$(echo "$JUL_BLOCK" | grep "HEAD" | head -n 1 | awk '{print $1}' || echo "0")
    J_POST=$(echo "$JUL_BLOCK" | grep "POST" | head -n 1 | awk '{print $1}' || echo "0")
    J_VOL=$(echo "$JUL_BLOCK" | grep -A 1 "8. Busiest Day" | tail -n 1 | awk '{print $1}' || echo "0")
    J_MAX=$(echo "$JUL_BLOCK" | grep "Max:" | awk '{print $2}' || echo "0")
    J_ERR=$(echo "$JUL_BLOCK" | grep -A 1 "5. Total 404 Errors" | tail -n 1 | awk '{print $1}' || echo "0")
    echo "July,$J_GET,$J_HEAD,$J_POST,$J_VOL,$J_MAX,$J_ERR"

    # August CSV Extraction (Using the exact GET fix that worked for your table)
    A_GET=$(echo "$AUG_BLOCK" | grep "GET" | head -n 1 | awk '{print $1}' || echo "0")
    A_HEAD=$(echo "$AUG_BLOCK" | grep "HEAD" | head -n 1 | awk '{print $1}' || echo "0")
    A_POST=$(echo "$AUG_BLOCK" | grep "POST" | head -n 1 | awk '{print $1}' || echo "0")
    A_VOL=$(echo "$AUG_BLOCK" | grep -A 1 "8. Busiest Day" | tail -n 1 | awk '{print $1}' || echo "0")
    A_MAX=$(echo "$AUG_BLOCK" | grep "Max:" | awk '{print $2}' || echo "0")
    A_ERR=$(echo "$AUG_BLOCK" | grep -A 1 "5. Total 404 Errors" | tail -n 1 | awk '{print $1}' || echo "0")
    echo "August,$A_GET,$A_HEAD,$A_POST,$A_VOL,$A_MAX,$A_ERR"
    
    echo "\`\`\`"

} > "$OUTPUT"

printf "Report generated successfully: %s\n" "$OUTPUT"