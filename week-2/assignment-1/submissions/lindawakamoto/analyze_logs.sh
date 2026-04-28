#!/bin/bash
set -euo pipefail


if [[ $# -lt 1 ]]; then
 echo "Usage: $0 data/*.log"
 exit 1
fi


OUTDIR="output"
mkdir -p "$OUTDIR"


export LC_ALL=C
export LANG=C


for LOGFILE in "$@"; do


OUTFILE="$OUTDIR/$(basename "$LOGFILE").analysis"
exec > >(tee "$OUTFILE")


echo "=================================================="
echo "ANALYZING LOG FILE: $LOGFILE"
echo "=================================================="


awk '


{
 total++


 host = $1
 ts = $4
 code = $9
 bytes = ($10 ~ /^[0-9]+$/ ? $10 : 0)


 method=""
 url=""


 if (match($0, /"[^"]+"/)) {
   req = substr($0, RSTART+1, RLENGTH-2)
   split(req, p, " ")
   method = p[1]
   url = p[2]
 }


 # ---------------- FILTERED COUNTS ----------------
 if (code != 404) {
   host_count[host]++
   if (url != "") url_count[url]++
 }


 method_count[method]++
 code_count[code]++


 if (code == 404) err404++


 if (host ~ /^[0-9]+\./) ip++
 else hostname++


 # ---------------- TIME PARSING ----------------
 gsub(/\[/,"",ts)
 split(ts,a,":")
 split(a[1],date,"/")


 day=date[1]
 mon=date[2]
 year=date[3]
 hour=a[2]


 if (mon=="Jan") mon="01"
 else if (mon=="Feb") mon="02"
 else if (mon=="Mar") mon="03"
 else if (mon=="Apr") mon="04"
 else if (mon=="May") mon="05"
 else if (mon=="Jun") mon="06"
 else if (mon=="Jul") mon="07"
 else if (mon=="Aug") mon="08"
 else if (mon=="Sep") mon="09"
 else if (mon=="Oct") mon="10"
 else if (mon=="Nov") mon="11"
 else if (mon=="Dec") mon="12"


 idx = year mon day hour
 seen[idx]=1


 day_key = day "/" mon "/" year
 day_count[day_key]++
 hour_count[hour]++


 # ---------------- SIZE ----------------
 if (bytes > 0) {
   total_bytes += bytes
   count_bytes++
   if (bytes > max_bytes) max_bytes = bytes
 }


 # ---------------- ERRORS ----------------
 if (code >= 400) {
   err_hour[hour]++
   err_host[host]++
 }
}


END {


# ==================================================
# BASIC ANALYSIS
# ==================================================
print "\n================ BASIC ANALYSIS ================\n"
print "Total requests:", total


# ---------------- TOP HOSTS ----------------
print "\nTop 10 hosts (excluding 404):"
for (h in host_count)
 print host_count[h], h | "sort -nr | head -10"
close("sort -nr | head -10")


# ---------------- IP VS HOSTNAME ----------------
printf "\nIP: %.2f%%\n", (ip/total)*100
printf "Hostname: %.2f%%\n", (hostname/total)*100


# ---------------- TOP URLS ----------------
print "\nTop 10 URLs (excluding 404):"
for (u in url_count)
 print url_count[u], u | "sort -nr | head -10"
close("sort -nr | head -10")


# ---------------- REQUEST TYPES ----------------
print "\nRequest methods:"
for (m in method_count)
 print method_count[m], m | "sort -nr"
close("sort -nr")


# ---------------- RESPONSE CODES ----------------
print "\nResponse codes:"
max_code=""
max_val=0


for (c in code_count) {
 printf "%d %s (%.2f%%)\n", code_count[c], c, (code_count[c]/total)*100
 if (code_count[c] > max_val) {
   max_val = code_count[c]
   max_code = c
 }
}


print "\nMost frequent response code:", max_code
print "Percentage:", (max_val/total)*100


print "\n404 errors:", err404


# ==================================================
# TIME ANALYSIS
# ==================================================
print "\n================ TIME ANALYSIS ================\n"


max_day=""; min_day=""
maxv=0; minv=1e12


for (d in day_count) {
 if (day_count[d] > maxv) { maxv=day_count[d]; max_day=d }
 if (day_count[d] < minv) { minv=day_count[d]; min_day=d }
}


print "Busiest day:", max_day


# exclude outage-like low activity days (<100 requests heuristic)
for (d in day_count) {
 if (day_count[d] < minv && day_count[d] > 100) {
   minv = day_count[d]
   min_day = d
 }
}


print "Quietest day (excluding outage days):", min_day


print "\nPeak hours:"
maxh=0; maxhour=""
minh=1e12; minhour=""


for (h in hour_count) {
 if (hour_count[h] > maxh) { maxh = hour_count[h]; maxhour = h }
 if (hour_count[h] < minh) { minh = hour_count[h]; minhour = h }
}


print "Peak hour:", maxhour
print "Quiet hour:", minhour


# ==================================================
# ADVANCED ANALYSIS
# ==================================================
print "\n================ ADVANCED ANALYSIS ================\n"


print "Max response size:", max_bytes
print "Average response size:", (count_bytes?total_bytes/count_bytes:0)


print "\nError patterns by hour:"
for (h in err_hour)
 print err_hour[h], h | "sort -nr"
close("sort -nr")


print "\nTop error hosts:"
for (h in err_host)
 print err_host[h], h | "sort -nr | head -10"
close("sort -nr | head -10")


# ==================================================
# OUTAGE DETECTION
# ==================================================
print "\n================ HURRICANE OUTAGE ANALYSIS ================\n"


for (k in seen)
 print k > "/tmp/times.tmp"
close("/tmp/times.tmp")


system("sort -n /tmp/times.tmp > /tmp/times_sorted.tmp")


prev=""
outage_count=0
total_missing=0


while ((getline curr < "/tmp/times_sorted.tmp") > 0) {


 if (prev != "") {


   gap = curr - prev - 1


   if (gap > 0) {


     outage_count++
     total_missing += gap


     py=substr(prev,1,4); pm=substr(prev,5,2); pd=substr(prev,7,2); ph=substr(prev,9,2)
     cy=substr(curr,1,4); cm=substr(curr,5,2); cd=substr(curr,7,2); ch=substr(curr,9,2)


     print "Outage #" outage_count
     print "Start    :", pd "/" pm "/" py ":" ph ":00"
     print "End      :", cd "/" cm "/" cy ":" ch ":00"
     print "Duration :", gap " hours"
     print "-----------------------------"
   }
 }


 prev = curr
}


close("/tmp/times_sorted.tmp")


print "\n================ FINAL SUMMARY ================\n"
print "TOTAL OUTAGES:", outage_count
print "TOTAL MISSING HOURS:", total_missing


print "\nEND"


}
' "$LOGFILE"


done
