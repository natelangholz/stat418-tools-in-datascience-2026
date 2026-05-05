# Basic Analysis
echo "Starting basic analysis of NASA log files..."

# Part 1: Top 10 Hosts

# part a: Jul95
echo "Top 10 Hosts in NASA_Jul95.log:"
awk '$9 != 404 {print $1}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 10

# part b: Aug95
echo "Top 10 Hosts in NASA_Aug95.log:"
awk '$9 != 404 {print $1}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 10



# Part 2: IP vs Hostname

# part a: Jul95
echo "Calculating percentage of requests from IP addresses vs hostnames in NASA_Jul95.log:"
num_ip_jul=$(awk '{print $1}' NASA_Jul95.log | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | wc -l)
num_logs_jul=$(wc -l < NASA_Jul95.log)
percent_ip_jul=$((num_ip_jul * 100 / num_logs_jul))
echo "Percentage of requests from IP addresses in NASA_Jul95.log: $percent_ip_jul%"
percent_host_jul=$((100 - percent_ip_jul))
echo "Percentage of requests from hostnames in NASA_Jul95.log: $percent_host_jul%"

# part b: Aug95
echo "Calculating percentage of requests from IP addresses vs hostnames in NASA_Aug95.log:"
num_ip_aug=$(awk '{print $1}' NASA_Aug95.log | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' | wc -l)
num_logs_aug=$(wc -l < NASA_Aug95.log)
percent_ip_aug=$((num_ip_aug * 100 / num_logs_aug))
echo "Percentage of requests from IP addresses in NASA_Aug95.log: $percent_ip_aug%"
percent_host_aug=$((100 - percent_ip_aug))
echo "Percentage of requests from hostnames in NASA_Aug95.log: $percent_host_aug%"



# Part 3: Top 10 requests

# part a: Jul95
echo "Top 10 URLs in NASA_Jul95.log:"
awk '$9 != 404 {print $7}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 10

# part b: Aug95
echo "Top 10 URLs in NASA_Aug95.log:"
awk '$9 != 404 {print $7}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 10



# Part 4: Request types

# part a: Jul95
echo "Most frequent HTTP methods in NASA_Jul95.log:"
awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -rn

# part b: Aug95
echo "Most frequent HTTP methods in NASA_Aug95.log:"
awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -rn



# Part 5: 404 errors

# part a: Jul95
echo "Number of 404 errors in NASA_Jul95.log:"
awk '$9 == 404' NASA_Jul95.log | wc -l

# part b: Aug95
echo "Number of 404 errors in NASA_Aug95.log:"
awk '$9 == 404' NASA_Aug95.log | wc -l



# Part 6: Response codes

# part a: Jul95
echo "Most frequent response code in NASA_Jul95.log:"
awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1
echo "Calculating percentage of Jul95 responses:"
num_inst_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
percent_inst_jul=$((num_inst_jul * 100 / num_logs_jul))
echo "Percentage of most frequent response code in NASA_Jul95.log: $percent_inst_jul%"

# part b: Aug95
echo "Most frequent response code in NASA_Aug95.log:"
awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1
echo "Calculating percentage of Aug95 responses:"
num_inst_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
percent_inst_aug=$((num_inst_aug * 100 / num_logs_aug))
echo "Percentage of most frequent response code in NASA_Aug95.log: $percent_inst_aug%"





# Time-Based Analysis

# Part 7: Peak hours

# part a: Jul95
echo "Top five active hours in NASA_Jul95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 5
echo "Top five quiet hours in NASA_Jul95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 5

# part b: Aug95
echo "Top five active hours in NASA_Aug95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 5
echo "Top five quiet hours in NASA_Aug95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[2] != "") print t[2]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 5



# Part 8: Busiest day

# part a: Jul95
echo "Busiest day in NASA_Jul95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1

# part b: Aug95
echo "Busiest day in NASA_Aug95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1



# Part 9: Quietest Day

# part a: Jul95
echo "Quietest day in NASA_Jul95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Jul95.log | sort | uniq -c | sort -n | head -n 1

# part b: Aug95
echo "Quietest day in NASA_Aug95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c | sort -n | head -n 1




# Advanced Analysis

# Part 10: Hurricane Outage
echo "Request Distribution by Day in NASA_Aug95.log:"
awk -F'[][]' '{split($2, t, ":"); if (t[1] != "") print t[1]}' NASA_Aug95.log | sort | uniq -c
echo "While the quietest August day in part 9 is 26/Aug/1995, there was no data on 02/Aug/1995, which represents the Hurricane Erin outage."
echo "Hurricane data outage start:"
hur_start=$(
awk -F'[][]' '{
  split($2, a, "[:/ ]");
  date = a[1] "/" a[2] "/" a[3];
  if (date == "01/Aug/1995") print $2;
}' NASA_Aug95.log | sort -t: -k2,2n -k3,3n -k4,4n | tail -n 1)
echo "$hur_start"
echo "end:"
hur_end=$(
awk -F'[][]' '{
  split($2, a, "[:/ ]");
  date = a[1] "/" a[2] "/" a[3];
  if (date == "03/Aug/1995") print $2;
}' NASA_Aug95.log | sort -t: -k2,2n -k3,3n -k4,4n | head -n 1)
echo "$hur_end"

awk -v s="$hur_start" -v e="$hur_end" '
BEGIN {
  m["Jan"]=1; m["Feb"]=2; m["Mar"]=3; m["Apr"]=4;
  m["May"]=5; m["Jun"]=6; m["Jul"]=7; m["Aug"]=8;
  m["Sep"]=9; m["Oct"]=10; m["Nov"]=11; m["Dec"]=12;

  split(s, a, "[:/ ]");
  t1 = mktime(a[3] " " m[a[2]] " " a[1] " " a[4] " " a[5] " " a[6]);

  split(e, b, "[:/ ]");
  t2 = mktime(b[3] " " m[b[2]] " " b[1] " " b[4] " " b[5] " " b[6]);

  print t2 - t1;
}'



# Part 11: Response Size

# part a: Largest response size

# part 1: Jul95
echo "The largest response size(bytes) in NASA_Jul95.log is:"
awk '$9 != 404 {print $NF}' NASA_Jul95.log | sort -rn | head -n 1

# part 2: Aug95
echo "The largest response size(bytes) in NASA_Aug95.log is:"
awk '$9 != 404 {print $NF}' NASA_Aug95.log | sort -rn | head -n 1

# part b: Average response size

# part 1: Jul95
echo "The average response size(bytes) in NASA_Jul95.log is:"
awk '$9 != 404 {sum += $NF; count ++} END {if (count > 0) print sum / count; else print 0}' NASA_Jul95.log

# part 2: Aug95
echo "The average response size(bytes) in NASA_Aug95.log is:"
awk '$9 != 404 {sum += $NF; count ++} END {if (count > 0) print sum / count; else print 0}' NASA_Aug95.log



# Part 12: Error Patterns

# part a: Jul95
jul_errors=$(awk '$9 == 404' NASA_Jul95.log | wc -l)
echo "There are $jul_errors 404 errors in NASA_Jul95.log"

# part 1: Host Analysis
echo "Top 5 hosts causing 404 errors in NASA_Jul95.log:"
awk '$9 == 404 {print $1}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 5
top_host=$(awk '$9 == 404 {print $1}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
host_errors=$(awk '$9 == 404 {print $1}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
error_percentage=$(awk -v a="$host_errors" -v b="$jul_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The top host, $top_host, was responsible for $error_percentage% of the 404 errors."

# part 2: URL Analysis
echo "Top 5 URLs causing 404 errors in NASA_Jul95.log:"
awk '$9 == 404 {print $7}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 5
top_url=$(awk '$9 == 404 {print $7}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
url_errors=$(awk '$9 == 404 {print $7}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
error_percentage=$(awk -v a="$url_errors" -v b="$jul_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The top URL, $top_url, was responsible for $error_percentage% of the 404 errors."

# part 3: Request Type Analysis
echo "Top 5 request types causing 404 errors in NASA_Jul95.log:"
awk '$9 == 404 {print $6}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 5
top_request_type=$(awk '$9 == 404 {print $6}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
request_type_errors=$(awk '$9 == 404 {print $6}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
error_percentage=$(awk -v a="$request_type_errors" -v b="$jul_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The top request type, $top_request_type, was responsible for $error_percentage% of the 404 errors."
# GET
get_requests=$(awk '$6 == "\"GET"' NASA_Jul95.log | wc -l)
tot_obs=$(wc -l < NASA_Jul95.log) 
get_percentage=$(awk -v a="$get_requests" -v b="$tot_obs" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "However, GET requests accounted for $get_percentage% of all requests in NASA_Jul95.log"
# no error get
noerror_get_requests=$(awk -F\" '{split($3, f, " "); status = f[2]; split($2, a, " "); 
if (a[1] == "GET" && status != 404) n++} END {print n}' NASA_Jul95.log)
tot_obs=$(wc -l < NASA_Jul95.log) 
noerror_get_percentage=$(awk -v a="$noerror_get_requests" -v b="$tot_obs" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "And, GET requests accounted for $noerror_get_percentage% of no error requests in NASA_Jul95.log"
nonerror_get_percentage=$(awk -v a="$noerror_get_requests" -v b="$get_requests" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "So while GET requests are the most common request type causing 404 errors, they are also the most common request type overall, and a significant portion of GET requests do not result in 404 errors at $nonerror_get_percentage%."

# part 4: Hour Analysis
echo "Top 5 hours causing 404 errors in NASA_Jul95.log:"
awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " "); 
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); print t[4]}}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 5
echo "The top hours for 404 errors in NASA_Jul95.log occur between 11 and 16 hours(excluding 13/1pm)."
echo "From part 7b, the busiest hours in NASA_Jul95.log are similarly between 11 and 16 hours, which suggests that the 404 errors are more likely to occur during busy hours, indicating potential server overload."
# percentage of errors between 11 and 16 hours
error_11_16=$(awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " "); 
status = ""; for (i in f) {if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]}
if (status == 404) {split($2, t, "[:/ ]"); hour = t[4]
if (hour >= 11 && hour <= 16) print hour}}' NASA_Jul95.log | wc -l)
busy_error_percentage=$(awk -v a="$error_11_16" -v b="$jul_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The percentage of 404 errors that occur between 11 and 16 hours in NASA_Jul95.log is: $busy_error_percentage%"
# percentage of busy hour requests that are errors
busy_hour_requests=$(awk -F'[][]' '{split($2, t, "[:/]"); hour = t[4]; if (hour >= 11 && hour <= 16) print $0}' NASA_Jul95.log | wc -l)
busy_hour_error_percentage=$(awk -v a="$error_11_16" -v b="$busy_hour_requests" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The percentage of requests that occur between 11 and 16 hours in NASA_Jul95.log that result in 404 errors is: $busy_hour_error_percentage%"
echo "The most errors occur during the busy hours, however, the busy hours only account for $busy_error_percentage% of errors, and only $busy_hour_error_percentage% of requests during busy hours result in 404 errors."

# part 5: Date Analysis
echo "Top 5 dates causing 404 errors in NASA_Jul95.log:"
awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " ");
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); print t[1] "/" t[2] "/" t[3]}}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 5
error_day=$(awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " ");
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); print t[1] "/" t[2] "/" t[3]}}' NASA_Jul95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
error_day_errors=$(awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " ");
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); date = t[1] "/" t[2] "/" t[3]; if (date == "'"$error_day"'") print $0}}' NASA_Jul95.log | wc -l)
error_day_percentage=$(awk -v a="$error_day_errors" -v b="$jul_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')  
echo "The top date for 404 errors in NASA_Jul95.log is: $error_day with $error_day_percentage% of all 404 errors."

# Conclusion
echo "In July 1995, there were $jul_errors 404 errors.  On the surface, the most highly correlated variables are the request type and hour."
echo "GET requests are the most common request type causing 404 errors, however, most requests are GET request and of GET requests, the majority do not result in 404 errors."
echo "The most common hours for 404 errors are between hours 11 and 16, but the hours are also the most high traffic hours and the majority of requests during the busy hours did not return errors."



# part b: Aug95
aug_errors=$(awk '$9 == 404' NASA_Aug95.log | wc -l)
echo "There are $aug_errors 404 errors in NASA_Aug95.log"

# part 1: Host Analysis
echo "Top 5 hosts causing 404 errors in NASA_Aug95.log:"
awk '$9 == 404 {print $1}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 5
top_host=$(awk '$9 == 404 {print $1}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
host_errors=$(awk '$9 == 404 {print $1}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
error_percentage=$(awk -v a="$host_errors" -v b="$aug_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The top host, $top_host, was responsible for $error_percentage% of the 404 errors."

# part 2: URL Analysis
echo "Top 5 URLs causing 404 errors in NASA_Aug95.log:"
awk '$9 == 404 {print $7}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 5
top_url=$(awk '$9 == 404 {print $7}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
url_errors=$(awk '$9 == 404 {print $7}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
error_percentage=$(awk -v a="$url_errors" -v b="$aug_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The top URL, $top_url, was responsible for $error_percentage% of the 404 errors."

# part 3: Request Type Analysis
echo "Top 5 request types causing 404 errors in NASA_Aug95.log:"
awk '$9 == 404 {print $6}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 5
top_request_type=$(awk '$9 == 404 {print $6}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
request_type_errors=$(awk '$9 == 404 {print $6}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $1}')
error_percentage=$(awk -v a="$request_type_errors" -v b="$aug_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The top request type, $top_request_type, was responsible for $error_percentage% of the 404 errors."
# GET
get_requests=$(awk '$6 == "\"GET"' NASA_Aug95.log | wc -l)
tot_obs=$(wc -l < NASA_Aug95.log) 
get_percentage=$(awk -v a="$get_requests" -v b="$tot_obs" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "However, GET requests accounted for $get_percentage% of all requests in NASA_Aug95.log."
# no error get
noerror_get_requests=$(awk -F\" '{split($3, f, " "); status = f[2]; split($2, a, " "); 
if (a[1] == "GET" && status != 404) n++} END {print n}' NASA_Aug95.log)
tot_obs=$(wc -l < NASA_Aug95.log) 
noerror_get_percentage=$(awk -v a="$noerror_get_requests" -v b="$tot_obs" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "And, GET requests accounted for $noerror_get_percentage% of no error requests in NASA_Aug95.log"
nonerror_get_percentage=$(awk -v a="$noerror_get_requests" -v b="$get_requests" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "So while GET requests are the most common request type causing 404 errors, they are also the most common request type overall, and a significant portion of GET requests do not result in 404 errors at $nonerror_get_percentage%."

# part 4: Hour Analysis
echo "Top 5 hours causing 404 errors in NASA_Aug95.log:"
awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " "); 
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); print t[4]}}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 5
error_hours=$(awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " "); 
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); print t[4]}}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 5 | awk '{print $2}' | paste -sd,)
echo "The top hours for 404 errors in NASA_Aug95.log occur during $error_hours hours."
# percentage of errors in error hours
error_hour_count=$(awk -F'[][]' -v hours="$error_hours" '
BEGIN {n = split(hours, h, ","); for(i = 1; i <= n; i++) top[h[i]] = 1}
{split($0, q, "\""); split(q[3], f, " ");
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); hour = t[4]
if (hour in top) print hour}}' NASA_Aug95.log | wc -l)
busy_error_percentage=$(awk -v a="$error_hour_count" -v b="$aug_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The percentage of 404 errors that occur in the top hours in NASA_Aug95.log is: $busy_error_percentage%"

# part 5: Date Analysis
echo "Top 5 dates causing 404 errors in NASA_Aug95.log:"
awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " ");
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); print t[1] "/" t[2] "/" t[3]}}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 5
error_day=$(awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " ");
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); print t[1] "/" t[2] "/" t[3]}}' NASA_Aug95.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')
error_day_errors=$(awk -F'[][]' '{split($0, q, "\""); split(q[3], f, " ");
status = ""; for (i in f) if (f[i] ~ /^[0-9][0-9][0-9]$/) status = f[i]
if (status == 404) {split($2, t, "[:/ ]"); date = t[1] "/" t[2] "/" t[3]; if (date == "'"$error_day"'") print $0}}' NASA_Aug95.log | wc -l)
error_day_percentage=$(awk -v a="$error_day_errors" -v b="$aug_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')  
echo "The top date for 404 errors in NASA_Aug95.log is: $error_day with $error_day_percentage% of all 404 errors."
# end of month errors
# last 3 days
echo "The last three days of the month occured in the top days for 404 errors in NASA_Aug95.log, which suggests that there may be an end of month pattern for 404 errors."
end_errors=$(
    awk -F'[][]' '{
    split($0, q, /["]/)
    split(q[3], f, " ")
    
    status = ""
    for (i in f)
        if(f[i] ~ /^[0-9][0-9][0-9]$/)
            status = f[i]
    
    if (status == 404){
        split($2, t, "[:/ ]")
        day = t[1] + 0
        if (day >= 29)
            print
    }
    }' NASA_Aug95.log | wc -l
)
end_error_percentage=$(awk -v a="$end_errors" -v b="$aug_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The percentage of 404 errors that occur in the last three days of the month in NASA_Aug95.log is: $end_error_percentage%"
# last week
echo "While the last three days of the month accound for many 404 errors, the closest time unit is a week, so I also looked at the last week."
end_week_errors=$(
    awk -F'[][]' '{
    split($0, q, /["]/)
    split(q[3], f, " ")
    
    status = ""
    for (i in f)
        if(f[i] ~ /^[0-9][0-9][0-9]$/)
            status = f[i]
    
    if (status == 404){
        split($2, t, "[:/ ]")
        day = t[1] + 0
        if (day >= 25)
            print
    }
    }' NASA_Aug95.log | wc -l
)
end_week_error_percentage=$(awk -v a="$end_week_errors" -v b="$aug_errors" 'BEGIN {if (b > 0) print (a * 100 / b); else print 0}')
echo "The percentage of 404 errors that occur in the last week in NASA_Aug95.log is: $end_week_error_percentage%"

# Conclusion
echo "In August 1995, there were $aug_errors 404 errors.  On the surface, the most highly related variables are the request type and the date."
echo "GET requests are the most common request type causing 404 errors, however, most requests are GET request and of GET requests, the majority do not result in 404 errors."
echo "The most common dates for 404 errors tended to be at the end of the month with $end_week_error_percentage% of errors in the last week and $end_error_percentage% of errors in just the last three days, which suggests a potential end of month pattern for 404 errors."
echo "However, the end of month pattern may be confounded with the high traffic at the end of the month."

# Overall Conclusion
echo "overall, the most prominent relationship with 404 error quantity was the traffic during the time."
echo "As the traffic increased, the number of 404 errors tended to increase."

echo "End of basic analysis of NASA log files."









