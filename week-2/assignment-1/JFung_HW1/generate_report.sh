# Reporting
echo "Summary Statistics for NASA Log Analysis"

# Part 2: Summary statistics

# part a: Jul95
echo "NASA_Jul95.log Summary Statistics:"
tot_req_jul=$(wc -l < NASA_Jul95.log)
echo "There were $tot_req_jul requests in total."

# part 1: host

# part a: most
echo "The most active hosts were:"
awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_host_reqs_jul=$(awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 3 | awk '{s+=$1} END{print s}')
top_host_percent_jul=$((top_host_reqs_jul * 100 / tot_req_jul))
echo "The top three hosts appear to be from the same user under different account names, which accounted for $top_host_reqs_jul requests, which is $top_host_percent_jul% of the total requests."


# part b: least
one_req_host_jul=$(awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{if($1==1) print $2}' | wc -l)
one_req_host_percent_jul=$(awk -v a="$one_req_host_jul" -v b="$tot_req_jul" 'BEGIN {printf "%.2f", (a * 100) / b}')
echo "There were $one_req_host_jul hosts that made only one request, which accounts for $one_req_host_percent_jul% of all requests."

# part c: min, mean, median, stdev, max of requests per host
min_host_jul=$(awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_host_jul=$(awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_host_jul=$(awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_host_jul=$(awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_host_jul=$(awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $2}')
max_host_reqs_jul=$(awk '{print $1}' NASA_Jul95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $1}')
echo "The minimum number of requests per host was $min_host_jul requests for $one_req_host_jul hosts.  The mean was $mean_host_jul requests.  The median was $median_host_jul requests.  The standard deviation was $stdev_host_jul requests.  The maximum was $max_host_reqs_jul requests from $max_host_jul."
echo "Because the median is far less than the mean and the standard deviation is high, the requests distribution by user is highly right skewed, with a few hosts making many requests and many hosts making few requests."

# part 2: day(hist)

# part a: most
echo "The most active days were:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_day_reqs_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 3 | awk '{s+=$1} END{print s}')
top_day_percent_jul=$((top_day_reqs_jul * 100 / tot_req_jul))
echo "The top three most active days accounted for $top_day_reqs_jul requests, which is $top_day_percent_jul% of the total requests."

# part b: least
echo "The least active days were:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
low_day_reqs_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 3 | awk '{s+=$1} END{print s}')
low_day_percent_jul=$((low_day_reqs_jul * 100 / tot_req_jul))
echo "The three least active days accounted for $low_day_reqs_jul requests, which is $low_day_percent_jul% of the total requests."

# part c: mean/median day
mean_days_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort -n | 
awk '{sum+=$1; count++} END {print sum/count}')
median_days_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort -n | 
awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
echo "The mean request day was $mean_days_jul, and the median was $median_days_jul, indicating more requests at the beginning of the month rather than the end."
echo "The result is consistent with the most and least active day lists."

# part d: min, mean, median, stdev, max of requests per day
min_day_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $2}')
min_day_reqs_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_day_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_day_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_day_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')    
max_day_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $2}')
max_day_reqs_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $1}')
echo "The minimum number of requests per day was $min_day_reqs_jul requests on $min_day_jul.  The mean was $mean_day_jul requests.  The median was $median_day_jul requests.  The standard deviation was $stdev_day_jul requests.   The maximum was $max_day_reqs_jul requests on $max_day_jul."

# part 3: hour

# part a: most
echo "The most active hours were:"
awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_hour_reqs_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 3 | awk '{s+=$1} END{print s}')
top_hour_percent_jul=$((top_hour_reqs_jul * 100 / tot_req_jul))
echo "The top three most active hours accounted for $top_hour_reqs_jul requests, which is $top_hour_percent_jul% of the total requests."

# part b: least
echo "The least active hours were:"
awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
low_hour_reqs_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 3 | awk '{s+=$1} END{print s}')
low_hour_percent_jul=$((low_hour_reqs_jul * 100 / tot_req_jul))
echo "The three least active hours accounted for $low_hour_reqs_jul requests, which is $low_hour_percent_jul% of the total requests."

# part c: mean/median
mean_hours_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort -n | 
awk '{sum+=$1; count++} END {print sum/count}')
median_hours_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort -n | 
awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
echo "The mean hour of request was $mean_hours_jul, and the median was $median_hours_jul."

# part d: min, mean, median, stdev, max of requests per hour
min_hour_reqs_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
min_hour_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $2}')
mean_hour_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_hour_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_hour_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_hour_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $2}')
max_hour_reqs_jul=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $1}')
echo "The minimum number of requests per hour was $min_hour_reqs_jul requests during hour $min_hour_jul.  The mean was $mean_hour_jul requests.  The median was $median_hour_jul requests. The standard deviation was $stdev_hour_jul requests.  The maximum was $max_hour_reqs_jul requests during hour $max_hour_jul."

# part 4: request type

# part a: chart
echo "Most frequent HTTP methods:"
awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 5 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_type_reqs_jul=$(awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
top_type_percent_jul=$((top_type_reqs_jul * 100 / tot_req_jul))
echo "The top request type accounted for $top_type_reqs_jul requests, which is $top_type_percent_jul% of the total requests."

# part b: min, mean, median, stdev, max of requests per type
min_type_jul=$(awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $2}')
min_type_reqs_jul=$(awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_type_jul=$(awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_type_jul=$(awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_type_jul=$(awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_type_jul=$(awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
max_type_reqs_jul=$(awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
echo "The minimum number of requests per type was $min_type_reqs_jul request of type $min_type_jul.  The mean was $mean_type_jul requests.  The median was $median_type_jul requests.  The standard deviation was $stdev_type_jul requests.  The maximum was $max_type_reqs_jul requests for $max_type_jul type requests."
echo "Because the median is far less than the mean and the standard deviation is high, the requests distribution by request type is highly right skewed, with a few request types making many requests but more types making few requests."


# part 5: URL

# part a: most 
echo "Most frequent URLs requested:"
awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
echo "The top 3 requested URLs are all images, and further investigating, part 3a from the basic analysis showed the top 7 URLs are all images."
top_url_reqs_jul=$(awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 7 | awk '{sum+=$1} END {print sum}')
top_url_percent_jul=$((top_url_reqs_jul * 100 / tot_req_jul))
echo "The top image URL requests accounted for $top_url_reqs_jul requests, which is $top_url_percent_jul% of the total requests."

# part b: least
one_req_url_jul=$(awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{if($1==1) print $2}' | wc -l)
one_req_url_percent_jul=$(awk -v a="$one_req_url_jul" -v b="$tot_req_jul" 'BEGIN {printf "%.2f", (a * 100) / b}')
echo "There were $one_req_url_jul URLs with only one request, which accounts for $one_req_url_percent_jul% of all requests."

# part c: min, mean, median, stdev, max of requests per URL
min_url_reqs_jul=$(awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_url_jul=$(awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_url_jul=$(awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_url_jul=$(awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_url_jul=$(awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
max_url_reqs_jul=$(awk '{print $7}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
echo "The minimum number of requests per URL was $min_url_reqs_jul request for $one_req_url_jul URLs.  The mean was $mean_url_jul requests.  The median was $median_url_jul request.  The standard deviation was $stdev_url_jul requests.  The maximum was $max_url_reqs_jul requests for the URL $max_url_jul."
echo "Because the median is far less than the mean and the standard deviation is high, the requests distribution by URL is highly right skewed, with a few requests for many URLs and many requests for few URLs."


# part 5: response code 

# part a: most
echo "Most frequent response codes:"
awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_code_reqs_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 7 | awk '{sum+=$1} END {print sum}')
top_code_percent_jul=$((top_code_reqs_jul * 100 / tot_req_jul))
echo "The top response code requests accounted for $top_code_reqs_jul requests, which is $top_code_percent_jul% of the total requests."

# part b: least
one_req_code_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{if($1==1) print $2}' | wc -l)
one_req_code_percent_jul=$(awk -v a="$one_req_code_jul" -v b="$tot_req_jul" 'BEGIN {printf "%.2f", (a * 100) / b}')
echo "There were $one_req_code_jul response codes returned to only one request, which accounts for $one_req_code_percent_jul% of all requests."

# part b: min, mean, median, stdev, max requests per status
min_code_reqs_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_code_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_code_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_code_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_code_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
max_code_reqs_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
echo "The minimum number of requests for a response code was $min_code_reqs_jul request for $one_req_code_jul response codes.  The mean was $mean_code_jul requests.  The median was $median_code_jul requests.  The standard deviation was $stdev_code_jul requests.  The maximum was $max_code_reqs_jul requests with a $max_code_jul response code."
echo "Because the median is far less than the mean and the standard deviation is high, the requests distribution by response code is highly right skewed, with many response codes returned only for one request and few response codes returned to many requests."


# part 6: bytes

# part a: most
echo "The largest responses in bytes were:"
awk '{size = ($NF == "-" ? 0 : $NF); print size, $6, $7}' NASA_Jul95.log | sort -k1,1nr | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'

# part b: least
no_resp_req_jul=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
no_resp_percent_jul=$((no_resp_req_jul * 100 / tot_req_jul))
echo "There were $no_resp_req_jul requests with a response size of 0 bytes, which accounts for $no_resp_percent_jul% of requests."

# part c: min, mean, median, stdev, max response size
min_resp_jul=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Jul95.log | sort |  head -n 1 | awk '{print $1}')
mean_resp_jul=$(awk '{size = ($NF == "-" ? 0 : $NF); sum += size; count ++} END {print sum/count}' NASA_Jul95.log)
median_resp_jul=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Jul95.log | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_resp_jul=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Jul95.log | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_resp_jul=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Jul95.log | sort -k1,1nr | head -n 1)
max_resp_req_jul=$(awk '{size = ($NF == "-" ? 0 : $NF); print size, $6, $7}' NASA_Jul95.log | sort -k1,1nr | head -n 1 | awk '{print $2, $3}')
echo "The minimum response size for a request was $min_resp_jul bytes for $no_resp_req_jul requests.  The mean size was $mean_resp_jul bytes.  The median was $median_resp_jul bytes.  The standard deviation was $stdev_resp_jul bytes.  The maximum was $max_resp_jul bytes from the request $max_resp_req_jul."
echo "Because the median is far less than the mean and the standard deviation is high, the response size distribution by request is highly right skewed, with many requests with small response sizes and few with large response sizes."




# part b: Aug95
echo "NASA_Aug95.log Summary Statistics:"
tot_req_aug=$(wc -l < NASA_Aug95.log)
echo "There were $tot_req_aug requests in total."

# part 1: host

# part a: most
echo "The most active hosts were:"
awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_host_reqs_aug=$(awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 3 | awk '{s+=$1} END{print s}')
top_host_percent_aug=$((top_host_reqs_aug * 100 / tot_req_aug))
echo "The top three hosts accounted for $top_host_reqs_aug requests, which is $top_host_percent_aug% of the total requests."

# part b: least
one_req_host_aug=$(awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{if($1==1) print $2}' | wc -l)
one_req_host_percent_aug=$(awk -v a="$one_req_host_aug" -v b="$tot_req_aug" 'BEGIN {printf "%.2f", (a * 100) / b}')
echo "There were $one_req_host_aug hosts that made only one request, which accounts for $one_req_host_percent_aug% of all requests."

# part c: min, mean, median, stdev, max of requests per host
min_host_aug=$(awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_host_aug=$(awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_host_aug=$(awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_host_aug=$(awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_host_aug=$(awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $2}')
max_host_reqs_aug=$(awk '{print $1}' NASA_Aug95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $1}')
echo "The minimum number of requests per host was $min_host_aug request for $one_req_host_aug hosts.  The mean was $mean_host_aug requests.  The median was $median_host_aug requests.  The standard deviation was $stdev_host_aug requests.  The maximum was $max_host_reqs_aug requests from $max_host_aug."
echo "Because the median is noticeably less than the mean and the standard deviation is high, the requests distribution by user is highly right skewed, with a few hosts making many requests and many hosts making few requests."

# part 2: day(hist)

# part a: most
echo "The most active days were:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_day_reqs_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 3 | awk '{s+=$1} END{print s}')
top_day_percent_aug=$((top_day_reqs_aug * 100 / tot_req_aug))
echo "The top three most active days are also the last three days of the month and accounted for $top_day_reqs_aug requests, which is $top_day_percent_aug% of the total requests."

# part b: least
echo "The least active days were:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
low_day_reqs_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 3 | awk '{s+=$1} END{print s}')
low_day_percent_aug=$((low_day_reqs_aug * 100 / tot_req_aug))
echo "The three least active days accounted for $low_day_reqs_aug requests, which is $low_day_percent_aug% of the total requests."

# part c: mean/median day
mean_days_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort -n | 
awk '{sum+=$1; count++} END {print sum/count}')
median_days_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort -n | 
awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
echo "The mean request day was $mean_days_aug, and the median was $median_days_aug, indicating more requests at the end of the month rather than the beginning."
echo "The result is consistent with the most active day list."

# part d: min, mean, median, stdev, max of requests per day
min_day_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $2}')
min_day_reqs_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_day_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_day_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_day_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')    
max_day_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $2}')
max_day_reqs_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $1}')
echo "The minimum number of requests per day was $min_day_reqs_aug requests on $min_day_aug.  The mean was $mean_day_aug requests.  The median was $median_day_aug requests.  The standard deviation was $stdev_day_aug requests.   The maximum was $max_day_reqs_aug requests on $max_day_aug."

# part 3: hour

# part a: most
echo "The most active hours were:"
awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_hour_reqs_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 3 | awk '{s+=$1} END{print s}')
top_hour_percent_aug=$((top_hour_reqs_aug * 100 / tot_req_aug))
echo "The top three most active hours accounted for $top_hour_reqs_aug requests, which is $top_hour_percent_aug% of the total requests."

# part b: least
echo "The least active hours were:"
awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
low_hour_reqs_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 3 | awk '{s+=$1} END{print s}')
low_hour_percent_aug=$((low_hour_reqs_aug * 100 / tot_req_aug))
echo "The three least active hours unsurprisingly occurred when people usually sleep and accounted for $low_hour_reqs_aug requests, which is $low_hour_percent_aug% of the total requests."

# part c: mean/median
mean_hours_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort -n | 
awk '{sum+=$1; count++} END {print sum/count}')
median_hours_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort -n | 
awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
echo "The mean hour of request was $mean_hours_aug, and the median was $median_hours_aug."

# part d: min, mean, median, stdev, max of requests per hour
min_hour_reqs_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
min_hour_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $2}')
mean_hour_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_hour_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_hour_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_hour_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $2}')
max_hour_reqs_aug=$(awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | tail -n 1 | awk '{print $1}')
echo "The minimum number of requests per hour was $min_hour_reqs_aug requests during hour $min_hour_aug.  The mean was $mean_hour_aug requests.  The median was $median_hour_aug requests. The standard deviation was $stdev_hour_aug requests.  The maximum was $max_hour_reqs_aug requests during hour $max_hour_aug."

# part 4: request type

# part a: chart
echo "Most frequent HTTP methods:"
awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 5 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_type_reqs_aug=$(awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
top_type_percent_aug=$((top_type_reqs_aug * 100 / tot_req_aug))
echo "The top request type accounted for $top_type_reqs_aug requests, which is $top_type_percent_aug% of the total requests."

# part b: min, mean, median, stdev, max of requests per type
min_type_aug=$(awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $2}')
min_type_reqs_aug=$(awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_type_aug=$(awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_type_aug=$(awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_type_aug=$(awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_type_aug=$(awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
max_type_reqs_aug=$(awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
echo "The minimum number of requests per type was $min_type_reqs_aug request of type $min_type_aug.  The mean was $mean_type_aug requests.  The median was $median_type_aug requests.  The standard deviation was $stdev_type_aug requests.  The maximum was $max_type_reqs_aug requests for $max_type_aug type requests."
echo "Because the median is far less than the mean and the standard deviation is high, the requests distribution by request type is highly right skewed, with a few request types making many requests but more types making few requests."


# part 5: URL

# part a: most
echo "Most frequent URLs requested:"
awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
echo "The top 3 requested URLs are all images, and further investigating, part 3b from the basic analysis showed the top 6 URLs are all images."
top_url_reqs_aug=$(awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 6 | awk '{sum+=$1} END {print sum}')
top_url_percent_aug=$((top_url_reqs_aug * 100 / tot_req_aug))
echo "The top image URL requests accounted for $top_url_reqs_aug requests, which is $top_url_percent_aug% of the total requests."

# part b: least
one_req_url_aug=$(awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{if($1==1) print $2}' | wc -l)
one_req_url_percent_aug=$(awk -v a="$one_req_url_aug" -v b="$tot_req_aug" 'BEGIN {printf "%.2f", (a * 100) / b}')
echo "There were $one_req_url_aug URLs with only one request, which accounts for $one_req_url_percent_aug% of all requests."

# part c: min, mean, median, stdev, max of requests per URL
min_url_reqs_aug=$(awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_url_aug=$(awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_url_aug=$(awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_url_aug=$(awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_url_aug=$(awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
max_url_reqs_aug=$(awk '{print $7}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
echo "The minimum number of requests per URL was $min_url_reqs_aug request for $one_req_url_aug URLs.  The mean was $mean_url_aug requests.  The median was $median_url_aug request.  The standard deviation was $stdev_url_aug requests.  The maximum was $max_url_reqs_aug requests for the URL $max_url_aug."
echo "Because the median is far less than the mean and the standard deviation is high, the requests distribution by URL is highly right skewed, with a few requests for many URLs and many requests for few URLs."


# part 5: response code 

# part a: most
echo "Most frequent response codes:"
awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 3 | awk '
{count[NR]=$1; host[NR]=$2; if($1>max) max=$1} END {width=50; for(i=1;i<=NR;i++) {bar=int((count[i]/max)*width); printf "%-20s | ", host[i]; for(j=0;j<bar;j++) printf "#"; printf " (%d)\n", count[i]}}'
top_code_reqs_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 7 | awk '{sum+=$1} END {print sum}')
top_code_percent_aug=$((top_code_reqs_aug * 100 / tot_req_aug))
echo "The top response code requests accounted for $top_code_reqs_aug requests, which is $top_code_percent_aug% of the total requests."

# part b: least
one_req_code_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{if($1==1) print $2}' | wc -l)
one_req_code_percent_aug=$(awk -v a="$one_req_code_aug" -v b="$tot_req_aug" 'BEGIN {printf "%.2f", (a * 100) / b}')
echo "There were $one_req_code_aug different response codes returned to only one request, which accounts for $one_req_code_percent_aug% of all requests."

# part b: min, mean, median, stdev, max requests per status
min_code_reqs_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1 | awk '{print $1}')
mean_code_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; count++} END {print sum/count}')
median_code_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_code_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_code_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
max_code_reqs_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
echo "The minimum number for requests for a response code was $min_code_reqs_aug request for $one_req_code_aug different response codes.  The mean was $mean_code_aug requests.  The median was $median_code_aug request.  The standard deviation was $stdev_code_aug requests.  The maximum was $max_code_reqs_aug requests with a $max_code_aug response code."
echo "Because the median is far less than the mean and the standard deviation is high, the requests distribution by response code is highly right skewed, with many response codes returned only for one request and few response codes returned to many requests."


# part 6: bytes

# part a: most
echo "The largest responses in bytes were:"
awk '{size = ($NF == "-" ? 0 : $NF); print size, $6, $7}' NASA_Aug95.log | sort -k1,1nr | head -n 3 

# part b: least
no_resp_req_aug=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
no_resp_percent_aug=$((no_resp_req_aug * 100 / tot_req_aug))
echo "There were $no_resp_req_aug requests with a response size of 0 bytes, which accounts for $no_resp_percent_aug% of requests."

# part c: min, mean, median, stdev, max response size
min_resp_aug=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Aug95.log | sort |  head -n 1 | awk '{print $1}')
mean_resp_aug=$(awk '{size = ($NF == "-" ? 0 : $NF); sum += size; count ++} END {print sum/count}' NASA_Aug95.log)
median_resp_aug=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Aug95.log | sort -n | awk '{a[NR] = $1} END {if (NR % 2 == 1) {print a[(NR + 1) / 2]} else {print (a[NR / 2] + a[NR / 2 + 1]) / 2}}')
stdev_resp_aug=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Aug95.log | awk '{sum+=$1; sumsq+=$1*$1; count++} END {mean=sum/count; print sqrt(sumsq/count - mean*mean)}')
max_resp_aug=$(awk '{size = ($NF == "-" ? 0 : $NF); print size}' NASA_Aug95.log | sort -k1,1nr | head -n 1)
max_resp_req_aug=$(awk '{size = ($NF == "-" ? 0 : $NF); print size, $6, $7}' NASA_Aug95.log | sort -k1,1nr | head -n 1 | awk '{print $2, $3}')
echo "The minimum response size for a request was $min_resp_aug bytes for $no_resp_req_aug requests.  The mean size was $mean_resp_aug bytes.  The median was $median_resp_aug bytes.  The standard deviation was $stdev_resp_aug bytes.  The maximum was $max_resp_aug bytes from the request $max_resp_req_aug."
echo "Because the median is far less than the mean and the standard deviation is high, the response size distribution by request is highly right skewed, with many requests with small response sizes and few with large response sizes."



# Part 3: Compare July and August activity

# part a: total obs
month_diff=$((tot_req_jul - tot_req_aug))
echo "July was more busy than August with $month_diff more requests."

# part b: most host
top_host_diff=$((top_host_reqs_jul - top_host_reqs_aug))
top_host_percent_diff=$(awk -v a="$top_host_percent_jul" -v b="$top_host_percent_aug" 'BEGIN {printf "%.4f", a - b}')
echo "The most active hosts were more active in July with $top_host_diff more requests and accounting for $top_host_percent_diff percentage point more of the month's total requests."  

# part c: one request host
one_req_host_diff=$((one_req_host_jul - one_req_host_aug))
one_req_host_percent_diff=$(awk -v a="$one_req_host_percent_aug" -v b="$one_req_host_percent_jul" 'BEGIN {printf "%.4f", a - b}')
echo "There were $one_req_host_diff more hosts that made only one request in July than in August; however, the percentage of requests from hosts who only made one request was $one_req_host_percent_diff percentage points higher in August."

# part d: per host
mean_host_diff=$(awk -v a="$mean_host_jul" -v b="$mean_host_aug" 'BEGIN {printf "%.4f", a - b}')
median_host_diff=$((median_host_jul - median_host_aug))
stdev_host_diff=$(awk -v a="$stdev_host_jul" -v b="$stdev_host_aug" 'BEGIN {printf "%.4f", a - b}')
max_host_diff=$(awk -v a="$max_host_reqs_jul" -v b="$max_host_reqs_aug" 'BEGIN {printf "%.4f", a - b}')
echo "The minimum number of requests per host was the same for both months, but the other metrics were higher in July matching the higher overall traffic in July."
echo "The mean was $mean_host_diff requests higher, and the median was $median_host_diff requests higher in July than August.  However, the standard deviation was $stdev_host_diff requests higher in July as well.  The maximum was also $max_host_diff requests higher in July than August."

# part e: most active day
top_day_diff=$((top_day_reqs_jul - top_day_reqs_aug))
top_day_percent_diff=$(awk -v a="$top_day_percent_jul" -v b="$top_day_percent_aug" 'BEGIN {printf "%.4f", a - b}')
echo "The most active days were more active in July with $top_day_diff more requests and accounting for $top_day_percent_diff percentage point more of the month's total requests."
echo "The most active days differed with the most active days of July at the beginning of the month, and the most active August days at the end of the month."

# part f: least active day
low_day_diff=$((low_day_reqs_jul - low_day_reqs_aug))
low_day_percent_diff=$(awk -v a="$low_day_percent_jul" -v b="$low_day_percent_aug" 'BEGIN {printf "%.4f", a - b}')
echo "The least active days were more active in July with $low_day_diff more requests; however, the least active days in August accounted for higher proportion of the total requests by $low_day_percent_diff percentage points."

# part g: average day
mean_days_diff=$(awk -v a="$mean_days_jul" -v b="$mean_days_aug" 'BEGIN {printf "%.4f", a - b}')
median_days_diff=$((median_days_jul - median_days_aug))
echo "The mean day of request was $mean_days_diff days higher in August than in July, and the median was $median_days_diff days higher in August than in July, indicating more requests at the end of the month rather than the beginning in August compared to July."

# part h: per day
min_day_diff=$((min_day_reqs_aug - min_day_reqs_jul))
mean_day_diff=$(awk -v a="$mean_day_jul" -v b="$mean_day_aug" 'BEGIN {printf "%.4f", a - b}')
median_day_diff=$(awk -v a="$median_day_jul" -v b="$median_day_aug" 'BEGIN {printf "%.4f", a - b}')
stdev_day_diff=$(awk -v a="$stdev_day_jul" -v b="$stdev_day_aug" 'BEGIN {printf "%.4f", a - b}')
max_day_diff=$((max_day_reqs_jul - max_day_reqs_aug))
echo "The minimum requests per day was $min_day_diff requests higher in August than in July, but the other metrics were higher in July matching the higher overall traffic in July.  The mean was $mean_day_diff requests higher, and the median was $median_day_diff requests higher in July than August.  However, the standard deviation was $stdev_day_diff requests higher in July as well.  The maximum was also $max_day_diff requests higher in July than August."

# part i: most active hour
top_hour_diff=$((top_hour_reqs_jul - top_hour_reqs_aug))
top_hour_percent_diff=$(awk -v a="$top_hour_percent_aug" -v b="$top_hour_percent_jul" 'BEGIN {printf "%.4f", a - b}')
echo "The most active hours in July were more active than the most active hours in August by $top_hour_diff requests; however, the most active hours in August accounted for $top_hour_percent_diff percentage points more of the total month requests than the most active hours in July."

# part j: least active hour
low_hour_diff=$((low_hour_reqs_jul - low_hour_reqs_aug))
low_hour_percent_diff=$(awk -v a="$low_hour_percent_aug" -v b="$low_hour_percent_jul" 'BEGIN {printf "%.4f", a - b}')
echo "The least active hours in July were more active than the least active hours in August by $low_hour_diff requests, but the respective quiet hours requests accounted for the same percentage of the months' total requests."

# part k: average hour
echo "The mean hour of request in July and August were similar, where July's metrics were $mean_hours_jul and $median_hours_jul, and August's metrics were $mean_hours_aug and $median_hours_aug."

# part l: per hour
min_hour_diff=$((min_hour_reqs_jul - min_hour_reqs_aug))
mean_hour_diff=$(awk -v a="$mean_hour_jul" -v b="$mean_hour_aug" 'BEGIN {printf "%.4f", a - b}')
median_hour_diff=$(awk -v a="$median_hour_jul" -v b="$median_hour_aug" 'BEGIN {printf "%.4f", a - b}')
stdev_hour_diff=$(awk -v a="$stdev_hour_jul" -v b="$stdev_hour_aug" 'BEGIN {printf "%.4f", a - b}')
max_hour_diff=$((max_hour_reqs_jul - max_hour_reqs_aug))
echo "Matching the overall traffic, the metrics were higher in July than August.  The minimum requests per hour was $min_hour_diff requests higher, the median $median_hour_diff requests higher, the mean $mean_hour_diff requests higher, the standard deviation $stdev_hour_diff requests higher, and the maximum $max_hour_diff requests higher in July than August."

# part m: most request type
top_type_diff=$((top_type_reqs_jul - top_type_reqs_aug))
echo "The most requent request types were the same for both months and accounted for the same percentage of total requests per month, but the most frequent request types in July accounted for $top_type_diff more requests than the most frequent request types in August."

# part n: per request type
mean_type_diff=$(awk -v a="$mean_type_jul" -v b="$mean_type_aug" 'BEGIN {printf "%.4f", a - b}')
median_type_diff=$((median_type_jul - median_type_aug))
stdev_type_diff=$(awk -v a="$stdev_type_jul" -v b="$stdev_type_aug" 'BEGIN {printf "%.4f", a - b}')
max_type_diff=$((max_type_reqs_jul - max_type_reqs_aug))
echo "The minimum number of requests per type was the same accross months, but the type was different.  Additionally, the response type distribution was the same with a heavy right skew."
echo "The mean was $mean_type_diff requests higher in July, but the median was $median_type_diff request higher in August than July.  The standard deviation was $stdev_type_diff requests higher in July and the maximum was also $max_type_diff requests higher in July than August."

# part o: most URL
top_url_diff=$((top_url_reqs_jul - top_url_reqs_aug))
top_url_percent_diff=$(awk -v a="$top_url_percent_aug" -v b="$top_url_percent_jul" 'BEGIN {printf "%.4f", a - b}')
echo "The most requested URLs were the same accross months and were all images.  The most requested images in August accounted for a higher percentage of the total month's reuqests than July by $top_url_percent_diff percentage points, but the most requested images in July accounted for $top_url_diff more requests than the most requested images in August."

# part p: one request URL
one_req_url_diff=$((one_req_url_jul - one_req_url_aug))
one_req_url_percent_diff=$(awk -v a="$one_req_url_percent_jul" -v b="$one_req_url_percent_aug" 'BEGIN {printf "%.4f", a - b}')
echo "There were $one_req_url_diff more URLs with only one request in July than in August accounting for $one_req_url_percent_diff percentage points higher of the total requests in July than in August."

# part q: per URL
mean_url_diff=$(awk -v a="$mean_url_aug" -v b="$mean_url_jul" 'BEGIN {printf "%.4f", a - b}')
stdev_url_diff=$(awk -v a="$stdev_url_aug" -v b="$stdev_url_jul" 'BEGIN {printf "%.4f", a - b}')
max_url_diff=$((max_url_reqs_jul - max_url_reqs_aug))
echo "The minimum number of requests per URL was the same for both months as well as the median and the right skew distribution shape."
echo "On the other hand, August had a higher mean by $mean_url_diff requests and a higher standard deviation by $stdev_url_diff requests, but the maximum was higher in July by $max_url_diff requests than August."

# part r: most response code
echo "The most frequent response codes were the same for both months and both accounted for $top_code_percent_jul percentage of the total requests in their respective months."

# part s: least response code
one_req_code_diff=$(awk -v a="$one_req_code_jul" -v b="$one_req_code_aug" 'BEGIN {printf "%.4f", a - b}')
echo "There were $one_req_code_diff more response codes returned to only one request in July than August, but the infrequent codes accounted for the same percentage of total requests $one_req_code_percent_aug%."

# part t: per code
mean_code_diff=$(awk -v a="$mean_code_aug" -v b="$mean_code_jul" 'BEGIN {printf "%.4f", a - b}')
stdev_code_diff=$(awk -v a="$stdev_code_jul" -v b="$stdev_code_aug" 'BEGIN {printf "%.4f", a - b}')
max_code_diff=$((max_code_jul - max_code_aug))
echo "The minimum number of requests for a response code was the same for both months $min_code_jul as well as the median $median_code_jul requests and the right skew distribution shape.  However, the mean was higher in August by $mean_code_diff requests, the standard deviation was higher in July by $stdev_code_diff requests, and the maximum was higher in July by $max_code_diff requests than August."

# part u: largest response
top_resp_diff=$((max_resp_jul - max_resp_aug))
echo "The largest response in bytes was larger in July than August by $top_resp_diff bytes, but the second and third largest reponses were the same in both months."

# part v: no response
no_resp_req_diff=$((no_resp_req_jul - no_resp_req_aug))
no_resp_percent_diff=$(awk -v a="$no_resp_percent_aug" -v b="$no_resp_percent_jul" 'BEGIN {printf "%.4f", a - b}')
echo "There were $no_resp_req_diff more requests with a response size of 0 bytes in July than August, but the percentage of requests with no response was $no_resp_percent_diff percentage points higher in August than in July."

# part w: per request size
mean_resp_diff=$(awk -v a="$mean_resp_jul" -v b="$mean_resp_aug" 'BEGIN {printf "%.4f", a - b}')
median_resp_diff=$((median_resp_aug - median_resp_jul))
stdev_resp_diff=$(awk -v a="$stdev_resp_jul" -v b="$stdev_resp_aug" 'BEGIN {printf "%.4f", a - b}')
max_resp_diff=$((max_resp_jul - max_resp_aug))
echo "The July size metrics were higher than August's where the mean was $mean_resp_diff bytes higher, the median was $median_resp_diff bytes higher, the standard deviation was $stdev_resp_diff bytes higher, and the maximum was $max_resp_diff bytes higher in July than August."









