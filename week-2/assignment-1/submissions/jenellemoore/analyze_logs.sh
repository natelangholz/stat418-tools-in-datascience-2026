# Basic Analysis

set -euo pipefail

echo "#1 Top 10 hosts"
echo "Top 10 hosts/IPs in July (excluding 404)"
awk '$9 != 404 {print $1}' NASA_Jul95.log | \
    sort | \
    uniq -c | \
    sort -rn | \
    sed -n '1,10p'

echo "Top 10 hosts/IPs in August (excluding 404)"
awk '$9 != 404 {print $1}' NASA_Aug95.log | \
    sort | \
    uniq -c | \
    sort -rn | \
    sed -n '1,10p'

echo
echo

echo "#2 IP vs Hostname - What percentage of requests came from IP addresses vs hostnames?"
echo "What percentage of requests came from IP addresses vs hostname for July?" 
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
echo "In July, 22.16% came from IP addresses and 77.84% came from hostnames."

echo

echo "What percentage of requests came from IP addresses vs hostname for August?" 
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
echo "In August, 28.44% came from IP addresses and 71.56% came from hostnames."

echo
echo

echo "#3 Top 10 requests - List the top 10 most requested URLs (exclude 404 errors)"
echo "Top 10 most requested URLs (excluding 404) for July"
awk '$9 != 404 {print $7}' NASA_Jul95.log | \
    LC_ALL=C sort | \
    uniq -c | \
    LC_ALL=C sort -rn | \
    sed -n '1,10p'

echo "Top 10 most requested URLs (excluding 404) for August"
awk '$9 != 404 {print $7}' NASA_Aug95.log | \
    LC_ALL=C sort | \
    uniq -c | \
    LC_ALL=C sort -rn | \
    sed -n '1,10p'

echo
echo

echo "#4 Request types - List the most frequent HTTP methods (GET, POST, etc.) with counts"
echo "Most frequent HTTP methods (GET, POST, etc.) for July"
LC_ALL=C awk '$6 ~ /^"(GET|POST|HEAD)$/ {print $6}' NASA_Jul95.log | \
    LC_ALL=C tr -d '"' | \
    LC_ALL=C sort | \
    uniq -c | \
    LC_ALL=C sort -rn 

echo "Most frequent HTTP methods (GET, POST, etc.) for August"
LC_ALL=C awk '$6 ~ /^"(GET|POST|HEAD)$/ {print $6}' NASA_Aug95.log | \
    LC_ALL=C tr -d '"' | \
    LC_ALL=C sort | \
    uniq -c | \
    LC_ALL=C sort -rn 

echo
echo
echo "#5 404 errors - How many 404 errors were reported?"
echo "404 errors reported in July"
awk '{print $9}' NASA_Jul95.log | \
    grep '^404$' | \
    wc -l
echo "10,714 404 errors were reported in July."

echo "404 errors reported in August"
awk '{print $9}' NASA_Aug95.log | \
    grep '^404$' | \
    wc -l
echo "9,978 404 errors were reported in August."

echo
echo

echo "#6 Response codes - What is the most frequent response code and what percentage of responses did it account for?"
echo "Most frequent response code and what percentage of responses did it account for in July?"
awk '{print $9}' NASA_Jul95.log | \
    grep -E '^[0-9]{3}$' > july_response_code.txt
    total=$(wc -l < july_response_code.txt)

    sort july_response_code.txt | \
    uniq -c | \
    sort -rn | \
    awk -v total="$total" '{printf "Response code: %s  Count: %d  Percentage: %.2f%%\n", $2, $1, ($1/total)*100}' | \
    sed -n '1,10p'
echo "Response code 200 accounted for 89.89% for all responses in July."

echo "Most frequent response code and what percentage of responses did it account for in August?"
awk '{print $9}' NASA_Aug95.log | \
    grep -E '^[0-9]{3}$' > aug_response_code.txt
    total=$(wc -l < aug_response_code.txt)

    sort aug_response_code.txt | \
    uniq -c | \
    sort -rn | \
    awk -v total="$total" '{printf "Response code: %s  Count: %d  Percentage: %.2f%%\n", $2, $1, ($1/total)*100}' | \
    sed -n '1,10p'
echo "Response code 200 accounted for 89.08% for all responses in August."

echo
echo
echo

# Time-Based Analysis
echo
echo "#7 Peak hours - What hours of the day see the most activity? When is it quiet?"
echo "Hourly Activity in July:"
awk '{ split($4, t, ":"); print t[2] }' NASA_Jul95.log | \
  sort | \
  uniq -c | \
  sort -rn | \
  awk '{printf "%s:00 - %d events\n", $2, $1}'

echo "The most activity occurs during the 14:00 hour."
echo "The least activity is seen during the 00:00 hour."

echo
echo "Hourly Activity in August:"
awk '{ split($4, t, ":"); print t[2] }' NASA_Aug95.log | \
  sort | \
  uniq -c | \
  sort -rn | \
  awk '{printf "%s:00 - %d events\n", $2, $1}'

echo "The most activity occurs during the 15:00 hour."
echo "The least activity is seen during the 04:00 hour."


echo
echo


echo "#8 Busiest day - Which date saw the most activity overall?"
echo "Busiest day in July:"
awk '{ split($4, t, ":"); print t[1] }' NASA_Jul95.log | \
  sort | \
  uniq -c | \
  sort -rn | \
  awk '{printf "%s:00 - %d events\n", $2, $1}'

echo "The busiet day in July was July 13, 1995." 

echo "Busiest day in August:"
awk '{ split($4, t, ":"); print t[1] }' NASA_Aug95.log | \
  sort | \
  uniq -c | \
  sort -rn | \
  awk '{printf "%s:00 - %d events\n", $2, $1}'

echo "The busiet day in August was August 31, 1995." 

echo
echo

echo "#9 Quietest day - Excluding outage dates, which date saw the least activity?"
echo "Quietest day (excluding outage dates) in July:"
awk '$9 < 500 || $9 >= 600 { split($4, t, ":"); print t[1] }' NASA_Jul95.log | \
  sort | \
  uniq -c | \
  sort -n | \
  awk '{printf "%s:00 - %d events\n", $2, $1}'

echo "The quietest day excluding outades was on July 28, 1995."

echo "Quietest day (excluding outage dates) in August:"
awk '$9 < 500 || $9 >= 600 { split($4, t, ":"); print t[1] }' NASA_Aug95.log | \
  sort | \
  uniq -c | \
  sort -n | \
  awk '{printf "%s:00 - %d events\n", $2, $1}'

echo "The quietest day excluding outades was on August 26, 1995."

echo
echo
echo

# Advanced Analysis
echo "#10 Hurricane outage - There was a hurricane in August causing a data outage. Identify the exact dates and times when data was not collected. How long was the outage?"
echo "Dates and times data not was collected in August"
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


echo "The hurricane resulted in a data outage lasting 1 day and 12 hours. The hurricane occured August 1, 1995 during the 15:00 hour and lasted untill August 3,1995 03:00 hour. "

echo
echo

echo "#11 Response size - What is the largest response (in bytes) and what is the average response size?"
echo "Largest response (in bytes) for July"
awk '$10 != "-" {print $10}' NASA_Jul95.log | \
    sort | \
    sort -n | \
    sed -n '$p'

echo "Largest response was 6,823,936 bytes."

echo "Average response size (in bytes) for July"

awk '$10 != "-" {sum += $10; count++} 
    END { 
        print "Average:", sum/count
        }' NASA_Jul95.log 

echo "The average response size was 20,624.90 bytes."

echo "Largest response (in bytes) for August"
awk '$10 != "-" {print $10}' NASA_Aug95.log | \
    sort | \
    sort -n | \
    sed -n '$p'

echo "Largest response was 3,421,948 bytes."

echo "Average response size (in bytes) for August"

awk '$10 != "-" {sum += $10; count++} 
    END { 
        print "Average:", sum/count
        }' NASA_Aug95.log 

echo "The average response size was 17,221 bytes."

echo
echo

echo "#12 Error patterns - Are there any patterns in when errors occur (time of day, specific hosts, etc.)?"
echo "Total error service codes in July"
awk '$9 ~ /^[45][0-9][0-9]$/ {print $9}' NASA_Jul95.log | \
    sort | \
    uniq -c | \
    sort -rn | \
    head -10 || true

echo "Total error service codes in August"
awk '$9 ~ /^[45][0-9][0-9]$/ {print $9}' NASA_Aug95.log | \
    sort | \
    uniq -c | \
    sort -rn | \
    head -10 || true

echo "The service code, 404, was the error that occured the most in July and August."

echo

echo "Top 10 hosts/IPs making error request in July"
awk '$9 ~ /^[45][0-9][0-9]$/ {print $1}' NASA_Jul95.log | \
    sort | \
    uniq -c | \
    sort -rn | \
    head -10 || true

echo "Top 10 hosts/IPs making error request in August"
awk '$9 ~ /^[45][0-9][0-9]$/ {print $1}' NASA_Aug95.log | \
    sort | \
    uniq -c | \
    sort -rn | \
    head -10 || true

echo "The top host that made an error request in July was hoohoo.ncsa.uiuc.edu. For August, 62 dialip-217.den.mmc.com."

echo

echo "Day with the most errors"
awk '$9 ~ /^[45][0-9][0-9]$/ { split($4, t, ":"); print t[1] }' NASA_Jul95.log NASA_Aug95.log | \
  sort | \
  uniq -c | \
  sort -rn | \
  head -10 | \
  awk '{printf "%s - %d events\n", $2, $1}'

echo "The days with the most errors in July and August were July 19, 1995 and August 30, 1995." 

echo

echo "Top specific day and hour error spikes"
awk '$9 ~ /^[45][0-9][0-9]$/ { split($4, t, ":"); print t[1], t[2] }' NASA_Jul95.log NASA_Aug95.log | \
  sort | \
  uniq -c | \
  sort -rn | \
  head -10 | \
  awk '{printf "%s %s:00 - %d events\n", $2, $3, $1}'

echo "The top hour of the day with the most errors in July and August were July 18, 1995 during the 15:00 hour and August 7, 1995 during the 02:00 hour." 

echo

echo "Top pages/resources with the most errors in July"
awk '$9 ~ /^[45][0-9][0-9]$/ {print $7}' NASA_Jul95.log | \
    LC_ALL=C sort | \
    uniq -c | \
    LC_ALL=C sort -rn | \
    head -10 || true

echo "Top pages/resources with the most errors in August"
awk '$9 ~ /^[45][0-9][0-9]$/ {print $7}' NASA_Aug95.log | \
    LC_ALL=C sort | \
    uniq -c | \
    LC_ALL=C sort -rn | \
    head -10 || true

echo "The top pages/resources with the most errors for both July and August were /pub/winvn.readme.txt. "
