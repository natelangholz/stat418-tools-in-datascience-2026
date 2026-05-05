#!/bin/bash
# generate_report.sh - Generate and analyze logs
# Usage: ./generate_report.sh <directory> <operation>

set -uo pipefail
export LC_ALL=C

{
# Open/create the report file
    echo "# Assignment 1: Web Server Log Analysis with Bash Report" 
    echo
    echo "This report summarizes the analysis of NASA web server logs from July and August 1995."
    echo "It compares overall request behavior, errors, and response codes across both months."
    echo
    echo "Debug check"
    echo "Checking whether input files exist:"
    ls -l NASA_Jul95.log NASA_Aug95.log 2>&1
    echo

    echo "## 1) Top 10 Hosts/IPs"
    echo
    echo "### Top 10 hosts in July (excluding 404 errors)"
    echo
    echo '```'
    awk '$9 != 404 {print $1}' NASA_Jul95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -10
    echo '```'
    echo
    echo "### Top 10 hosts in August (excluding 404 errors)"
    echo
    echo '```'
    awk '$9 != 404 {print $1}' NASA_Aug95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -10
    echo '```'
    echo

    echo "## 2) IP vs Hostname - What percentage of requests came from IP addresses vs hostnames?"
    echo
    echo "### What percentage of requests came from IP addresses vs hostname for July?"
    echo
    echo '```'
    awk '{print $1}' NASA_Jul95.log > all_july_hosts.txt

        total=$(wc -l < all_july_hosts.txt)
        ip=$(grep -Ec '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' all_july_hosts.txt)
        host=$(grep -Evc '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' all_july_hosts.txt)

        echo "Total requests: $total"
        echo "IP requests: $ip"
        echo "Hostname requests: $host"

    awk -v total="$total" -v ip="$ip" -v host="$host" 'BEGIN {
        printf "IP addresses: %.2f%%\n", (ip/total)*100
        printf "Hostnames: %.2f%%\n", (host/total)*100
        }'
    echo '```'
    echo
    echo "July Hostnames        | ####################  77.84%" 
    echo "July IP addresses     | #####                 22.16%"
    echo
    echo
    echo "### What percentage of requests came from IP addresses vs hostname for August?"
    echo
    echo '```'
    awk '{print $1}' NASA_Aug95.log > all_aug_hosts.txt

        total=$(wc -l < all_aug_hosts.txt)
        ip=$(grep -Ec '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' all_aug_hosts.txt)
        host=$(grep -Evc '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' all_aug_hosts.txt)

    echo "Total requests: $total"
    echo "IP requests: $ip"
    echo "Hostname requests: $host"

    awk -v total="$total" -v ip="$ip" -v host="$host" 'BEGIN {
        printf "IP addresses: %.2f%%\n", (ip/total)*100
        printf "Hostnames: %.2f%%\n", (host/total)*100
        }'
    echo '```'
    echo 
    echo "August Hostnames      | ##################    71.56%"
    echo "August IP addresses   | ######                28.44%"
    echo
    echo
    echo "## 3) Top 10 requested URLs (exclude 404 errors)"
    echo
    echo "### Top 10 most requested URLs (excluding 404) for July"
    echo
    echo '```'
    awk '$9 != 404 {print $7}' NASA_Jul95.log | \
         LC_ALL=C sort | \
        uniq -c | \
        LC_ALL=C sort -rn | \
        head -10
    echo '```'
    echo
    echo "### Top 10 most requested URLs (excluding 404) for August"
    echo
    echo '```'
    awk '$9 != 404 {print $7}' NASA_Aug95.log | \
        LC_ALL=C sort | \
        uniq -c | \
        LC_ALL=C sort -rn | \
        head -10
    echo '```'
    echo
    echo
    echo "## 4) Request types - List the most frequent HTTP methods (GET, POST, etc.) with counts"
    echo
    echo "### Most frequent HTTP methods (GET, POST, etc.) for July"
    echo
    echo '```'
    awk '$6 ~ /^"(GET|POST|HEAD)$/ {print $6}' NASA_Jul95.log | \
        tr -d '"' | \
        sort | \
        uniq -c | \
        sort -rn 
    echo '```'
    echo
    echo "### Most frequent HTTP methods (GET, POST, etc.) for August"
    echo
    echo '```'
    awk '$6 ~ /^"(GET|POST|HEAD)$/ {print $6}' NASA_Aug95.log | \
        tr -d '"' | \
        sort | \
        uniq -c | \
        sort -rn 
    echo '```'
    echo
    echo
    echo "## 5) 404 errors - How many 404 errors were reported?"
    echo
    echo "### 404 errors reported in July"
    echo
    echo '```'
    awk '{print $9}' NASA_Jul95.log | \
        grep '^404$' | \
        wc -l
    echo '```'
    echo
    echo "### 404 errors reported in August"
    echo
    echo '```'
    awk '{print $9}' NASA_Aug95.log | \
        grep '^404$' | \
        wc -l
    echo '```'
    echo
    echo "404 Error Rate"
    echo "July   | ###----------------- 14.2%"
    echo "August | #####--------------- 22.8%"
    echo
    echo
    echo "## 6) Response codes - What is the most frequent response code and what percentage of responses did it account for?"
    echo
    echo "### Most frequent response code and what percentage of responses did it account for in July?"
    echo
    echo '```'
    awk '{print $9}' NASA_Jul95.log | \
        grep -E '^[0-9]{3}$' > july_response_code.txt
        total=$(wc -l < july_response_code.txt)

        sort july_response_code.txt | \
        uniq -c | \
        sort -rn | \
        awk -v total="$total" '{printf "Response code: %s  Count: %d  Percentage: %.2f%%\n", $2, $1, ($1/total)*100}' | \
        head -10
    echo '```'
    echo
    echo "### Most frequent response code and what percentage of responses did it account for in August?"
    echo
    echo '```'
    awk '{print $9}' NASA_Aug95.log | \
        grep -E '^[0-9]{3}$' > aug_response_code.txt
        total=$(wc -l < aug_response_code.txt)

        sort aug_response_code.txt | \
        uniq -c | \
        sort -rn | \
        awk -v total="$total" '{printf "Response code: %s  Count: %d  Percentage: %.2f%%\n", $2, $1, ($1/total)*100}' | \
        head -10
    echo '```'
    echo
    echo
    echo ## "Time-Based Analysis:"
    echo
    echo "## 7) Peak hours - What hours of the day see the most activity? When is it quiet?"
    echo
    echo "### Hourly Activity in July:"
    echo
    echo '```'
    awk '{ split($4, t, ":"); print t[2] }' NASA_Jul95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        awk '{printf "%s:00 - %d events\n", $2, $1}'
    echo '```'
    echo "The most activity occurs during the 14:00 hour and the least activity is seen during the 00:00 hour."
    echo
    echo
    echo "### Hourly Activity in August:"
    echo
    echo '```'
    awk '{ split($4, t, ":"); print t[2] }' NASA_Aug95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        awk '{printf "%s:00 - %d events\n", $2, $1}'
    echo '```'
    echo "The most activity occurs during the 15:00 hour and the least activity is seen during the 04:00 hour."
    echo
    echo
    echo "## 8) Busiest day - Which date saw the most activity overall?"
    echo
    echo "### Busiest day in July:"
    echo
    echo '```'
    awk '{ split($4, t, ":"); print t[1] }' NASA_Jul95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        awk '{printf "%s:00 - %d events\n", $2, $1}'
    echo '```'
    echo "The busiet day in July was July 13, 1995."
    echo
    echo
    echo "### Busiest day in August:"
    echo
    echo '```'
    awk '{ split($4, t, ":"); print t[1] }' NASA_Aug95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        awk '{printf "%s:00 - %d events\n", $2, $1}'
    echo '```'
    echo "The busiet day in August was August 31, 1995."
    echo
    echo
    echo "## 9) Quietest day - Excluding outage dates, which date saw the least activity?"
    echo
    echo "### Quietest day (excluding outage dates) in July:"
    echo
    echo '```'
    awk '$9 < 500 || $9 >= 600 { split($4, t, ":"); print t[1] }' NASA_Jul95.log | \
        sort | \
        uniq -c | \
        sort -n | \
        awk '{printf "%s:00 - %d events\n", $2, $1}'
    echo '```'
    echo "The quietest day excluding outades was on July 28, 1995."
    echo
    echo
    echo "### Quietest day (excluding outage dates) in August:"
    echo
    echo '```'
    awk '$9 < 500 || $9 >= 600 { split($4, t, ":"); print t[1] }' NASA_Aug95.log | \
        sort | \
        uniq -c | \
        sort -n | \
        awk '{printf "%s:00 - %d events\n", $2, $1}'
    echo '```'
    echo "The quietest day excluding outades was on August 26, 1995."
    echo
    echo
    echo ## "Advanced Analysis"
    echo
    echo "## 10) Hurricane outage - There was a hurricane in August causing a data outage. Identify the exact dates and times when data was not collected. How long was the outage?"
    echo
    echo "### Dates and times data was not collected in August"
    echo
    echo '```'
    awk '{ split($4, t, ":" ); print substr(t[1], 2), t[2] }' NASA_Aug95.log | \
        sort | \
        uniq > dates_present_aug.txt 

        > all_dates_aug.txt
        for day in $(seq -w 1 31)
        do
            for hour in $(seq -w 0 23)
            do
                echo "$day/Aug/1995 $hour" >> all_dates_aug.txt
            done
        done

        grep -vxFf dates_present_aug.txt all_dates_aug.txt
    echo '```'
    echo "The hurricane resulted in a data outage lasting 1 day and 12 hours. The hurricane occured August 1, 1995 during the 15:00 hour and lasted untill August 3,1995 03:00 hour."
    echo
    echo
    echo "## 11) Response size - What is the largest response (in bytes) and what is the average response size?"
    echo
    echo "### Largest response (in bytes) for July"
    echo
    echo '```'
    awk '$10 != "-" {print $10}' NASA_Jul95.log | \
        sort | \
        sort -n | \
        tail -1
    echo '```'
    echo
    echo "Average response size (in bytes) for July"
    echo '```'
    awk '$10 != "-" {sum += $10; count++} 
        END { 
        print "Average:", sum/count
        }' NASA_Jul95.log 
    echo '```'
    echo
    echo "### Largest response (in bytes) for August"
    echo
    echo '```'
    awk '$10 != "-" {print $10}' NASA_Aug95.log | \
        sort | \
        sort -n | \
        tail -1
    echo '```'
    echo
    echo "### Average response size (in bytes) for August"
    echo
    echo '```'
    awk '$10 != "-" {sum += $10; count++} 
        END { 
        print "Average:", sum/count
        }' NASA_Aug95.log 
    echo '```'
    echo 
    echo "July Largest Response        | ####################  6,823,936 bytes" 
    echo "July Average Response        | ####                  20,624.90 bytes"
    echo
    echo "August Largest Response      | ##########            3,421,948 bytes"
    echo "August Average Response      | ####.                 17,221 bytes"
    echo
    echo
    echo "## 12) Error patterns - Are there any patterns in when errors occur (time of day, specific hosts, etc.)?"
    echo
    echo "### Total error service codes in July"
    echo
    echo '```'
    awk '$9 ~ /^[45][0-9][0-9]$/ {print $9}' NASA_Jul95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -10
    echo '```'
    echo
    echo "### Total error service codes in August"
    echo
    echo '```'
    awk '$9 ~ /^[45][0-9][0-9]$/ {print $9}' NASA_Aug95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -10
    echo '```'
    echo 
    echo "The service code, 404, was the error that occured the most in July and August."
    echo 
    echo
    echo "### Top 10 hosts/IPs making error request in July"
    echo '```'
    awk '$9 ~ /^[45][0-9][0-9]$/ {print $1}' NASA_Jul95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -10
    echo '```'
    echo
    echo "### Top 10 hosts/IPs making error request in August"
    echo
    echo '```'
    awk '$9 ~ /^[45][0-9][0-9]$/ {print $1}' NASA_Aug95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -10
    echo '```'
    echo 
    echo "The top host that made an error request in July was hoohoo.ncsa.uiuc.edu. For August, 62 dialip-217.den.mmc.com."
    echo
    echo
    echo "### Day with the most errors"
    echo
    echo '```'
    awk '$9 ~ /^[45][0-9][0-9]$/ { split($4, t, ":"); print t[1] }' NASA_Jul95.log NASA_Aug95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -10 | \
        awk '{printf "%s - %d events\n", $2, $1}'
    echo '```'
    echo 
    echo "The days with the most errors in July and August were July 19, 1995 and August 30, 1995."
    echo
    echo
    echo "### Top specific day and hour error spikes"
    echo
    echo '```'
    awk '$9 ~ /^[45][0-9][0-9]$/ { split($4, t, ":"); print t[1], t[2] }' NASA_Jul95.log NASA_Aug95.log | \
        sort | \
        uniq -c | \
        sort -rn | \
        head -10 | \
        awk '{printf "%s %s:00 - %d events\n", $2, $3, $1}'
    echo '```'
    echo 
    echo "The top hour of the day with the most errors in July and August were July 18, 1995 during the 15:00 hour and August 7, 1995 during the 02:00 hour."
    echo
    echo
    echo "### Top pages/resources with the most errors in July"
    echo
    echo '```'
    awk '$9 ~ /^[45][0-9][0-9]$/ {print $7}' NASA_Jul95.log | \
        LC_ALL=C sort | \
        uniq -c | \
        LC_ALL=C sort -rn | \
        head -10
    echo '```'
    echo 
    echo "Top pages/resources with the most errors in August"
    echo
    echo '```'
    awk '$9 ~ /^[45][0-9][0-9]$/ {print $7}' NASA_Aug95.log | \
        LC_ALL=C sort | \
        uniq -c | \
        LC_ALL=C sort -rn | \
        head -10
    echo '```'
    echo
    echo "The top pages/resources with the most errors for both July and August were /pub/winvn.readme.txt. "
    echo
    echo
    echo
    echo "## Summary Statistics"
    echo
    echo "Total requests were higher in August than July, showing increased server traffic."
    echo "The most common response code in both months was 200, meaning most requests were successful."
    echo "August had a higher 404 error rate (22.8%) compared to July (14.2%)."
    echo "Most requests used the GET HTTP method, with very few POST or HEAD requests."
    echo "Peak traffic occurred in the afternoon: July's busiest hour was 14:00 and August's busiest hour was 15:00."
    echo "The response file was larger in July (6,823,936 bytes) than August (3,421,948 bytes)."
    echo "Average response size was also larger in July."
    echo "August logs contained a major anomaly, a 1 day 12 hour outage, likely caused by Hurricane Erin."
    echo "Most common missing/error page in both months involved: /pub/winvn/readme.txt"
    echo
    echo "## Overall Conclusion"
    echo "The NASA server handled heavy traffic in both months with mostly successful responses. August showed more traffic and more client errors, while July served larger average files. The hurricane outage was the most significant unusual event in the dataset."
    echo
    echo

} > "REPORT.md"

