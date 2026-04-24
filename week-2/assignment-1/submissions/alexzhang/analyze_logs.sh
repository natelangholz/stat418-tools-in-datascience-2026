export LC_ALL=C

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $@"
}

#List the top 10 hosts/IPs making requests (exclude 404 errors)

log "Top 10 hosts/IPs making requests (excluding 404 errors) for July log:"
awk '$9 != 404 {print $1}' NASA_Jul95.log | sort | uniq -c | sort -nr | head -10

log "Top 10 hosts/IPs making requests (excluding 404 errors) for August log:"
awk '$9 != 404 {print $1}' NASA_Aug95.log | sort | uniq -c | sort -nr | head -10

# What percentage of requests came from IP addresses vs hostnames?

log "Percentage of requests from IP addresses vs hostnames for July log:"

total_requests_jul=$(wc -l < NASA_Jul95.log)
ip_requests_jul=$(awk '$1 ~ /^[0-9.]+$/ {count++} END {print count}' NASA_Jul95.log)
hostname_requests_jul=$((total_requests_jul - ip_requests_jul))
ip_percentage_jul=$(awk -v ip="$ip_requests_jul" -v total="$total_requests_jul" 'BEGIN {printf "%.2f", (ip/total)*100}')
hostname_percentage_jul=$(awk -v hostname="$hostname_requests_jul" -v total="$total_requests_jul" 'BEGIN {printf "%.2f", (hostname/total)*100}')
log "IP addresses: $ip_percentage_jul% ($ip_requests_jul requests)"
log "Hostnames: $hostname_percentage_jul% ($hostname_requests_jul requests)"

log "Percentage of requests from IP addresses vs hostnames for August log:"

total_requests_aug=$(wc -l < NASA_Aug95.log)
ip_requests_aug=$(awk '$1 ~ /^[0-9.]+$/ {count++} END {print count}' NASA_Aug95.log)
hostname_requests_aug=$((total_requests_aug - ip_requests_aug))
ip_percentage_aug=$(awk -v ip="$ip_requests_aug" -v total="$total_requests_aug" 'BEGIN {printf "%.2f", (ip/total)*100}')
hostname_percentage_aug=$(awk -v hostname="$hostname_requests_aug" -v total="$total_requests_aug" 'BEGIN {printf "%.2f", (hostname/total)*100}')
log "IP addresses: $ip_percentage_aug% ($ip_requests_aug requests)"
log "Hostnames: $hostname_percentage_aug% ($hostname_requests_aug requests)"

# List the top 10 most requested URLs (exclude 404 errors)

log "Top 10 most requested URLs (excluding 404 errors) for July log:"
awk '$9 != 404 {print $7}' NASA_Jul95.log | sort | uniq -c | sort -nr | head -10

log "Top 10 most requested URLs (excluding 404 errors) for August log:"
awk '$9 != 404 {print $7}' NASA_Aug95.log | sort | uniq -c | sort -nr | head -10

# List the most frequent HTTP methods (GET, POST, etc.) with counts

log "Most frequent HTTP methods with counts for July log:"
awk '{print $6}' NASA_Jul95.log | sort | uniq -c | sort -nr | head -3

log "Most frequent HTTP methods with counts for August log:"
awk '{print $6}' NASA_Aug95.log | sort | uniq -c | sort -nr | head -3

# How many 404 errors were reported?

log "Number of 404 errors for July log:"
awk '$9 == 404 {count++} END {print count}' NASA_Jul95.log

log "Number of 404 errors for August log:"
awk '$9 == 404 {count++} END {print count}' NASA_Aug95.log

# What is the most frequent response code and what percentage of responses did it account for?

log "Most frequent response code and percentage for July log:"
top_code_jul=$(awk '{print $9}' NASA_Jul95.log | sort | uniq -c | sort -nr | head -1)
total_requests_jul=$(wc -l < NASA_Jul95.log)
percentage_jul=$(awk -v count="$(echo $top_code_jul | awk '{print $1}')" -v total="$total_requests_jul" 'BEGIN {printf "%.2f", (count/total)*100}')
log "Response code: $(echo $top_code_jul | awk '{print $2}'), Count: $(echo $top_code_jul | awk '{print $1}'), Percentage: $percentage_jul%"


log "Most frequent response code and percentage for August log:"
top_code_aug=$(awk '{print $9}' NASA_Aug95.log | sort | uniq -c | sort -nr | head -1)
total_requests_aug=$(wc -l < NASA_Aug95.log)
percentage_aug=$(awk -v count="$(echo $top_code_aug | awk '{print $1}')" -v total="$total_requests_aug" 'BEGIN {printf "%.2f", (count/total)*100}')
log "Response code: $(echo $top_code_aug | awk '{print $2}'), Count: $(echo $top_code_aug | awk '{print $1}'), Percentage: $percentage_aug%"

# What hours of the day see the most activity? When is it quiet?

log "Hours of the day with most activity for July log:"
awk -F: '{print $2}' NASA_Jul95.log | sort | uniq -c | sort -nr | head -10
log "Hours of the day with most activity for August log:"
awk -F: '{print $2}' NASA_Aug95.log | sort | uniq -c | sort -nr | head -10

log "Hours of the day with least activity for July log:"
awk -F: '{print $2}' NASA_Jul95.log | sort | uniq -c | sort -n | awk '$1 > 100' | head -10
log "Hours of the day with least activity for August log:"
awk -F: '{print $2}' NASA_Aug95.log | sort | uniq -c | sort -n | awk '$1 > 100' | head -10

# Which date saw the most activity overall?

log "Date with the most activity for July log:"
awk -F: '{print $1}' NASA_Jul95.log | awk -F[ '{print $2}' | sort | uniq -c | sort -nr | head -1

log "Date with the most activity for August log:"
awk -F: '{print $1}' NASA_Aug95.log | awk -F[ '{print $2}' | sort | uniq -c | sort -nr | head -1

# Excluding outage dates, which date saw the least activity?

log "Date with the least activity for July log (excluding outage dates):"
awk -F: '{print $1}' NASA_Jul95.log | awk -F[ '{print $2}' | sort | uniq -c | sort -n | awk '$1 > 100' | head -1

log "Date with the least activity for August log (excluding outage dates):"
awk -F: '{print $1}' NASA_Aug95.log | awk -F[ '{print $2}' | sort | uniq -c | sort -n | awk '$1 > 100' | head -1

# There was a hurricane in August causing a data outage. Identify the exact dates and times when data was not collected. How long was the outage?

log "Data outage periods for August log:"
gawk '
BEGIN {
    split("Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec", m)
    for (i=1; i<=12; i++) month[m[i]] = i
}

{
    split(substr($4,2), a, "[:/]")
    t = mktime(a[3]" "month[a[2]]" "a[1]" "a[4]" "a[5]" "a[6])

    if (prev) {
        gap = t - prev
        if (gap > max) {
            max = gap
            s = prev
            e = t
        }
    }
    prev = t
}

END {
    hours = int(max / 3600)
    mins  = int((max % 3600) / 60)
    secs  = max % 60

    print "=== Data Outage Detected ==="
    print "Last log before outage :", strftime("%Y-%m-%d %H:%M:%S", s)
    print "First log after outage :", strftime("%Y-%m-%d %H:%M:%S", e)
    printf "Outage duration        : %d hours, %d minutes, %d seconds\n", hours, mins, secs
}
' NASA_Aug95.log

# What is the largest response (in bytes) and what is the average response size?

log "Largest response size and average response size for July log:"
awk '
$NF ~ /^[0-9]+$/ {
    sum += $NF
    count++

    if ($NF > max) {
        max = $NF
    }
}

END {
    print "Largest response size:", max, "bytes"
    print "Average response size:", sum/count, "bytes"
}
' NASA_Jul95.log

log "Largest response size and average response size for August log:"
awk '
$NF ~ /^[0-9]+$/ {
    sum += $NF
    count++

    if ($NF > max) {
        max = $NF
    }
}

END {
    print "Largest response size:", max, "bytes"
    print "Average response size:", sum/count, "bytes"
}
' NASA_Aug95.log

# Are there any patterns in when errors occur (time of day, specific hosts, etc.)?

log "Host patterns in when errors occur for July log:"
awk '
$9 ~ /^[45][0-9][0-9]$/ {
    count[$1]++
}
END {
    for (h in count)
        print h, count[h]
}
' NASA_Jul95.log | sort -k2 -nr | head -10

log "Hour patterns in when errors occur for July log:"
awk '
$9 ~ /^[45][0-9][0-9]$/ {
    gsub(/\[/,"",$4)
    split($4, t, ":")
    hour = t[2]
    count[hour]++
}
END {
    for (h in count)
        print h, count[h]
}
' NASA_Jul95.log | sort -k2 -nr | head -10


log "Host patterns in when errors occur for August log:"
awk '
$9 ~ /^[45][0-9][0-9]$/ {
    count[$1]++
}
END {
    for (h in count)
        print h, count[h]
}
' NASA_Aug95.log | sort -k2 -nr | head -10

log "Hour patterns in when errors occur for August log:"
awk '
$9 ~ /^[45][0-9][0-9]$/ {
    gsub(/\[/,"",$4)
    split($4, t, ":")
    hour = t[2]
    count[hour]++
}
END {
    for (h in count)
        print h, count[h]
}
' NASA_Aug95.log | sort -k2 -nr | head -10