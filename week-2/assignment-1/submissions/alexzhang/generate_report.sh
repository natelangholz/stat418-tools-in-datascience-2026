export LC_ALL=C
REPORT="report.md"

JULY="NASA_Jul95.log"
AUG="NASA_Aug95.log"

# calculations for month comparison
jul_total=$(wc -l < $JULY)
aug_total=$(wc -l < $AUG)

jul_4xx=$(awk '$9 ~ /^4/ {count++} END {print count+0}' $JULY)
aug_4xx=$(awk '$9 ~ /^4/ {count++} END {print count+0}' $AUG)
jul_5xx=$(awk '$9 ~ /^5/ {count++} END {print count+0}' $JULY)
aug_5xx=$(awk '$9 ~ /^5/ {count++} END {print count+0}' $AUG)

jul_top=$(awk '{print $9}' $JULY | sort | uniq -c | sort -nr | head -1)
aug_top=$(awk '{print $9}' $AUG | sort | uniq -c | sort -nr | head -1)

# used single redirect to write everything to the report file
{
echo "# NASA Web Log Analysis Report"
echo "Generated on $(date)"
echo ""

echo "## Summary"
echo "This report analyzes NASA web logs from July and August 1995, focusing on traffic patterns, error behavior, and a major outage event in August."
echo ""

echo "## Key Findings"

echo "- A significant outage occurred in August lasting ~37 hours."
echo "- Errors are concentrated among a small subset of hosts."
echo "- Error frequency varies by hour, with peaks during high traffic periods."
echo "- Both months showed zero traffic from 12 AM to 9 AM."
echo "- August shows reduced traffic due to outage compared to July."
echo ""

echo "## July Summary Statistics"
echo ""
echo "### Overall Activity"
echo "- Total requests: $jul_total"
echo "- 4xx errors: $jul_4xx ($(awk -v c="$jul_4xx" -v t="$jul_total" 'BEGIN {printf "%.2f", (c/t)*100}')%)"
echo "- 5xx errors: $jul_5xx ($(awk -v c="$jul_5xx" -v t="$jul_total" 'BEGIN {printf "%.2f", (c/t)*100}')%)"
echo "- 404 errors: $(awk '$9 == 404 {count++} END {print count+0}' $JULY)"
echo "- Most common response code: $(echo $jul_top | awk '{print $2}') ($(echo $jul_top | awk '{print $1}') requests, $(awk -v count="$(echo $jul_top | awk '{print $1}')" -v total="$jul_total" 'BEGIN {printf "%.2f", (count/total)*100}')%)"
echo ""
echo "### Top 5 Hosts/IPs"
awk '$9 != 404 {print $1}' $JULY | sort | uniq -c | sort -nr | head -5 | awk '{print "- " $2 ": " $1 " requests"}'
echo ""
echo "### Peak Activity Hours"
echo "- Most active hours: $(awk '{gsub(/\[/,"",$4); split($4,t,":"); print t[2]}' $JULY | sort | uniq -c | sort -nr | head -5 | awk '{printf "%02d:00 ", $2}' | sed 's/ $//')"
echo ""
echo "### HTTP Methods"
awk '{print $6}' $JULY | sort | uniq -c | sort -nr | awk '{print "- " $2 ": " $1 " requests"}' | head -3
echo ""

echo "## August Summary Statistics"
echo ""
echo "### Overall Activity"
echo "- Total requests: $aug_total"
echo "- 4xx errors: $aug_4xx ($(awk -v c="$aug_4xx" -v t="$aug_total" 'BEGIN {printf "%.2f", (c/t)*100}')%)"
echo "- 5xx errors: $aug_5xx ($(awk -v c="$aug_5xx" -v t="$aug_total" 'BEGIN {printf "%.2f", (c/t)*100}')%)"
echo "- 404 errors: $(awk '$9 == 404 {count++} END {print count+0}' $AUG)"
echo "- Most common response code: $(echo $aug_top | awk '{print $2}') ($(echo $aug_top | awk '{print $1}') requests, $(awk -v count="$(echo $aug_top | awk '{print $1}')" -v total="$aug_total" 'BEGIN {printf "%.2f", (count/total)*100}')%)"
echo ""
echo "### Top 5 Hosts/IPs"
awk '$9 != 404 {print $1}' $AUG | sort | uniq -c | sort -nr | head -5 | awk '{print "- " $2 ": " $1 " requests"}'
echo ""
echo "### Peak Activity Hours"
echo "- Most active hours: $(awk '{gsub(/\[/,"",$4); split($4,t,":"); print t[2]}' $AUG | sort | uniq -c | sort -nr | head -5 | awk '{printf "%02d:00 ", $2}' | sed 's/ $//')"
echo ""
echo "### HTTP Methods"
awk '{print $6}' $AUG | sort | uniq -c | sort -nr | awk '{print "- " $2 ": " $1 " requests"}' | head -3
echo ""

echo "## July vs August Comparison"
echo ""

# Total requests
echo "### Total Requests"
echo "- July: $jul_total requests"
echo "- August: $aug_total requests"
echo "- Difference: $(($jul_total - $aug_total)) fewer requests in August ($(awk -v a="$aug_total" -v j="$jul_total" 'BEGIN {printf "%.1f", (1-a/j)*100}')% decrease)"
echo ""

# Error rates (4xx and 5xx)
echo "### Error Analysis"

echo "- July 4xx errors: $jul_4xx ($(awk -v c="$jul_4xx" -v t="$jul_total" 'BEGIN {printf "%.2f", (c/t)*100}')%)"
echo "- August 4xx errors: $aug_4xx ($(awk -v c="$aug_4xx" -v t="$aug_total" 'BEGIN {printf "%.2f", (c/t)*100}')%)"
echo "- July 5xx errors: $jul_5xx ($(awk -v c="$jul_5xx" -v t="$jul_total" 'BEGIN {printf "%.2f", (c/t)*100}')%)"
echo "- August 5xx errors: $aug_5xx ($(awk -v c="$aug_5xx" -v t="$aug_total" 'BEGIN {printf "%.2f", (c/t)*100}')%)"
echo ""

# Top response codes
echo "### Most Common Response Code"
echo "- July: Response code $(echo $jul_top | awk '{print $2}') ($(echo $jul_top | awk '{print $1}') requests)"
echo "- August: Response code $(echo $aug_top | awk '{print $2}') ($(echo $aug_top | awk '{print $1}') requests)"
echo ""

# Traffic patterns - peak hours
echo "### Peak Traffic Hours"
echo "- July (Top 3 hours): $(awk '{gsub(/\[/,"",$4); split($4,t,":"); print t[2]}' $JULY | sort | uniq -c | sort -nr | head -3 | awk '{printf "%02d:00 ", $2}' | sed 's/ $//')"
echo "- August (Top 3 hours): $(awk '{gsub(/\[/,"",$4); split($4,t,":"); print t[2]}' $AUG | sort | uniq -c | sort -nr | head -3 | awk '{printf "%02d:00 ", $2}' | sed 's/ $//')"

# ascii visualizations of error frequency
echo "## Errors by Hour in July (ASCII Chart)"

awk '
$9 ~ /^[45]/ {
    gsub(/\[/,"",$4)
    split($4,t,":")
    h=t[2]
    count[h]++
}
END {
    for (i=0;i<24;i++) {
        bar=""
        for (j=0;j<count[i]/50;j++) bar=bar "#"
        printf "%02d: %s (%d)\n\n", i, bar, count[i]
    }
}
' $JULY

echo "## Errors by Hour in August (ASCII Chart)"

awk '
$9 ~ /^[45]/ {
    gsub(/\[/,"",$4)
    split($4,t,":")
    h=t[2]
    count[h]++
}
END {
    for (i=0;i<24;i++) {
        bar=""
        for (j=0;j<count[i]/50;j++) bar=bar "#"
        printf "%02d: %s (%d)\n\n", i, bar, count[i]
    }
}
' $AUG

# full output from analyze_logs.sh, probably don't need all of this but just added to show output of analyze_logs.sh since I kinda calculated the statistics again
echo "## Full Analysis Output"
echo '```'
./analyze_logs.sh
echo '```'

} > "$REPORT"