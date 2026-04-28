#!/bin/bash

mkdir -p results

# ===== July =====
echo "July log analysis" > results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "404 errors:" >> results/NASA_Jul95_summary.txt
LC_ALL=C grep ' 404 ' data/NASA_Jul95.log | wc -l >> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Request types:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk -F'"' '{
    split($2, a, " ")
    if (a[1] ~ /^[A-Z]+$/) print a[1]
}' data/NASA_Jul95.log | LC_ALL=C sort | uniq -c | LC_ALL=C sort -rn \
>> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Top 10 hosts excluding 404:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '$9 != 404 {print $1}' data/NASA_Jul95.log \
| LC_ALL=C sort | uniq -c | LC_ALL=C sort -rn | head -10 \
>> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "IP vs Hostname:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '{
    total++
    if ($1 ~ /^[0-9.]+$/) ip++
    else host++
}
END {
    printf "IP: %d %.2f%%\n", ip, ip * 100 / total
    printf "Hostname: %d %.2f%%\n", host, host * 100 / total
}' data/NASA_Jul95.log >> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Top 10 requests excluding 404:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk -F'"' '$3 !~ /^ 404 / {
    split($2, a, " ")
    if (a[2] ~ /^\//) print a[2]
}' data/NASA_Jul95.log | LC_ALL=C sort | uniq -c | LC_ALL=C sort -rn | head -10 \
>> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Most frequent response code:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '{
    count[$9]++
}
END {
    max = 0
    total = 0
    code = ""
    for (i in count) {
        total += count[i]
        if (count[i] > max) {
            max = count[i]
            code = i
        }
    }
    printf "%s %d %.2f%%\n", code, max, max * 100 / total
}' data/NASA_Jul95.log >> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Peak hour:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '{
    hour = substr($4, 14, 2)
    count[hour]++
}
END {
    max = 0
    peak = ""
    for (h in count) {
        if (count[h] > max) {
            max = count[h]
            peak = h
        }
    }
    printf "%s %d\n", peak, max
}' data/NASA_Jul95.log >> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Busiest day:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '{
    day = substr($4, 2, 11)
    count[day]++
}
END {
    max = 0
    best = ""
    for (d in count) {
        if (count[d] > max) {
            max = count[d]
            best = d
        }
    }
    printf "%s %d\n", best, max
}' data/NASA_Jul95.log >> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Quietest day excluding outage dates:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '{
    day = substr($4, 2, 11)
    hour = substr($4, 14, 2)
    count[day]++
    key = day " " hour
    if (!(key in seen)) {
        seen[key] = 1
        hours[day]++
    }
}
END {
    min = -1
    quiet = ""
    for (d in count) {
        if (hours[d] == 24) {
            if (min == -1 || count[d] < min) {
                min = count[d]
                quiet = d
            }
        }
    }
    printf "%s %d\n", quiet, min
}' data/NASA_Jul95.log >> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Response size:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '{
    if ($10 != "-" && $10 ~ /^[0-9]+$/) {
        total += $10
        count++
        if ($10 > max) max = $10
    }
}
END {
    printf "Largest: %d\n", max
    printf "Average: %.2f\n", total / count
}' data/NASA_Jul95.log >> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Error patterns:" >> results/NASA_Jul95_summary.txt

echo "Errors by hour:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '$9 >= 400 {
    hour = substr($4, 14, 2)
    count[hour]++
}
END {
    for (h in count) print h, count[h]
}' data/NASA_Jul95.log | LC_ALL=C sort -k2 -rn | head -5 >> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

echo "Hosts with most errors:" >> results/NASA_Jul95_summary.txt
LC_ALL=C awk '$9 >= 400 {print $1}' data/NASA_Jul95.log \
| LC_ALL=C sort | uniq -c | LC_ALL=C sort -rn | head -5 \
>> results/NASA_Jul95_summary.txt
echo "" >> results/NASA_Jul95_summary.txt

# ===== August =====
echo "August log analysis" > results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "404 errors:" >> results/NASA_Aug95_summary.txt
LC_ALL=C grep ' 404 ' data/NASA_Aug95.log | wc -l >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Request types:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk -F'"' '{
    split($2, a, " ")
    if (a[1] ~ /^[A-Z]+$/) print a[1]
}' data/NASA_Aug95.log | LC_ALL=C sort | uniq -c | LC_ALL=C sort -rn \
>> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Top 10 hosts excluding 404:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '$9 != 404 {print $1}' data/NASA_Aug95.log \
| LC_ALL=C sort | uniq -c | LC_ALL=C sort -rn | head -10 \
>> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "IP vs Hostname:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '{
    total++
    if ($1 ~ /^[0-9.]+$/) ip++
    else host++
}
END {
    printf "IP: %d %.2f%%\n", ip, ip * 100 / total
    printf "Hostname: %d %.2f%%\n", host, host * 100 / total
}' data/NASA_Aug95.log >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Top 10 requests excluding 404:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk -F'"' '$3 !~ /^ 404 / {
    split($2, a, " ")
    if (a[2] ~ /^\//) print a[2]
}' data/NASA_Aug95.log | LC_ALL=C sort | uniq -c | LC_ALL=C sort -rn | head -10 \
>> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Most frequent response code:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '{
    count[$9]++
}
END {
    max = 0
    total = 0
    code = ""
    for (i in count) {
        total += count[i]
        if (count[i] > max) {
            max = count[i]
            code = i
        }
    }
    printf "%s %d %.2f%%\n", code, max, max * 100 / total
}' data/NASA_Aug95.log >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Peak hour:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '{
    hour = substr($4, 14, 2)
    count[hour]++
}
END {
    max = 0
    peak = ""
    for (h in count) {
        if (count[h] > max) {
            max = count[h]
            peak = h
        }
    }
    printf "%s %d\n", peak, max
}' data/NASA_Aug95.log >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Busiest day:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '{
    day = substr($4, 2, 11)
    count[day]++
}
END {
    max = 0
    best = ""
    for (d in count) {
        if (count[d] > max) {
            max = count[d]
            best = d
        }
    }
    printf "%s %d\n", best, max
}' data/NASA_Aug95.log >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Quietest day excluding outage dates:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '{
    day = substr($4, 2, 11)
    hour = substr($4, 14, 2)
    count[day]++
    key = day " " hour
    if (!(key in seen)) {
        seen[key] = 1
        hours[day]++
    }
}
END {
    min = -1
    quiet = ""
    for (d in count) {
        if (hours[d] == 24) {
            if (min == -1 || count[d] < min) {
                min = count[d]
                quiet = d
            }
        }
    }
    printf "%s %d\n", quiet, min
}' data/NASA_Aug95.log >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Hurricane outage:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '{
    stamp = substr($4, 2, 20)
    day = substr($4, 2, 2) + 0
    hour = substr($4, 14, 2) + 0
    min = substr($4, 17, 2) + 0
    sec = substr($4, 20, 2) + 0
    now = (day - 1) * 86400 + hour * 3600 + min * 60 + sec

    if (NR > 1) {
        gap = now - prev
        if (gap > maxgap) {
            maxgap = gap
            start = prevstamp
            finish = stamp
        }
    }

    prev = now
    prevstamp = stamp
}
END {
    days = int(maxgap / 86400)
    rem = maxgap % 86400
    hours = int(rem / 3600)
    rem = rem % 3600
    mins = int(rem / 60)
    secs = rem % 60

    printf "Largest gap: %s -> %s\n", start, finish
    printf "Duration: %d days %d hours %d minutes %d seconds\n", days, hours, mins, secs
}' data/NASA_Aug95.log >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Response size:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '{
    if ($10 != "-" && $10 ~ /^[0-9]+$/) {
        total += $10
        count++
        if ($10 > max) max = $10
    }
}
END {
    printf "Largest: %d\n", max
    printf "Average: %.2f\n", total / count
}' data/NASA_Aug95.log >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Error patterns:" >> results/NASA_Aug95_summary.txt

echo "Errors by hour:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '$9 >= 400 {
    hour = substr($4, 14, 2)
    count[hour]++
}
END {
    for (h in count) print h, count[h]
}' data/NASA_Aug95.log | LC_ALL=C sort -k2 -rn | head -5 >> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "Hosts with most errors:" >> results/NASA_Aug95_summary.txt
LC_ALL=C awk '$9 >= 400 {print $1}' data/NASA_Aug95.log \
| LC_ALL=C sort | uniq -c | LC_ALL=C sort -rn | head -5 \
>> results/NASA_Aug95_summary.txt
echo "" >> results/NASA_Aug95_summary.txt

echo "done"

