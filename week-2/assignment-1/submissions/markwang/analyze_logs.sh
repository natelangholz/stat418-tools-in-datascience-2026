#!/bin/bash
# analyze_logs.sh - Analyze NASA web server logs
# Answers questions about hosts, requests, response codes, time-based patterns, and errors

set -e

LOG_FILE="${1:-}"

if [[ -z "${LOG_FILE}" ]]; then
    echo "Usage: $0 <log_file>"
    exit 1
fi

if [[ ! -f "${LOG_FILE}" ]]; then
    echo "Error: Log file not found: ${LOG_FILE}"
    exit 1
fi

echo "Analyzing: ${LOG_FILE}"
echo ""

# Basic Analysis

echo "Basic Analysis"
echo ""

# Top 10 hosts (exclude 404 errors)
echo "Top 10 Hosts (excluding 404 errors):"
awk '$9 != 404' "${LOG_FILE}" | awk '{print $1}' | sort | uniq -c | sort -rn | head -10 | awk '{print $2, "(" $1 " requests)"}'
echo ""

# IP vs Hostname percentage
echo "IP Addresses vs Hostnames:"
total_requests=$(wc -l < "${LOG_FILE}")
ip_requests=$(awk '{
    if ($1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/) {
        count++
    }
}
END {
    print count
}' "${LOG_FILE}")
hostname_requests=$((total_requests - ip_requests))
ip_percent=$(awk "BEGIN {printf \"%.2f\", ($ip_requests / $total_requests) * 100}")
hostname_percent=$(awk "BEGIN {printf \"%.2f\", ($hostname_requests / $total_requests) * 100}")
echo "  IP Addresses: ${ip_requests} (${ip_percent}%)"
echo "  Hostnames: ${hostname_requests} (${hostname_percent}%)"
echo ""

# Top 10 requests (exclude 404 errors)
echo "Top 10 Most Requested URLs (excluding 404 errors):"
awk '$9 != 404' "${LOG_FILE}" | awk -F'"' '{print $2}' | awk '{print $2}' | sort | uniq -c | sort -rn | head -10 | awk '{print $2, "(" $1 " requests)"}'
echo ""

# HTTP methods
echo "HTTP Methods (with counts):"
awk -F'"' '{print $2}' "${LOG_FILE}" | awk '{print $1}' | sort | uniq -c | sort -rn | awk '{print $2, $1}'
echo ""

# 404 errors
echo "404 Errors:"
error_404=$(awk '$9 == 404' "${LOG_FILE}" | wc -l)
error_404_percent=$(awk "BEGIN {printf \"%.2f\", ($error_404 / $total_requests) * 100}")
echo "  Total 404 errors: ${error_404} (${error_404_percent}%)"
echo ""

# Response codes
echo "Response Code Distribution:"
awk '{print $9}' "${LOG_FILE}" | sort | uniq -c | sort -rn | awk '{
    print "  Code " $2 ": " $1 " responses"
}'
echo ""

# Most frequent response code and percentage
most_frequent_code=$(awk '{print $9}' "${LOG_FILE}" | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
most_frequent_count=$(awk '{print $9}' "${LOG_FILE}" | sort | uniq -c | sort -rn | head -1 | awk '{print $1}')
most_frequent_percent=$(awk "BEGIN {printf \"%.2f\", ($most_frequent_count / $total_requests) * 100}")
echo "Most frequent response code: ${most_frequent_code} (${most_frequent_percent}% of all responses)"
echo ""

# Time-based Analysis

echo "Time-based Analysis"
echo ""

# Peak hours
echo "Peak Hours (most requests):"
awk '{
    # Extract timestamp between [ and ]
    start = index($0, "[") + 1
    end = index($0, "]") - 1
    timestamp = substr($0, start, end - start + 1)
    split(timestamp, parts, ":")
    hour = parts[2]
    print hour
}' "${LOG_FILE}" | sort | uniq -c | sort -rn | head -5 | awk '{printf "  %s:00 - %s requests\n", $2, $1}'
echo ""

echo "Quiet Hours (least requests):"
awk '{
    # Extract timestamp between [ and ]
    start = index($0, "[") + 1
    end = index($0, "]") - 1
    timestamp = substr($0, start, end - start + 1)
    split(timestamp, parts, ":")
    hour = parts[2]
    print hour
}' "${LOG_FILE}" | sort | uniq -c | sort -n | head -5 | awk '{printf "  %s:00 - %s requests\n", $2, $1}'
echo ""

# Busiest day
echo "Busiest Day:"
awk '{
    # Extract timestamp between [ and ]
    start = index($0, "[") + 1
    end = index($0, "]") - 1
    timestamp = substr($0, start, end - start + 1)
    split(timestamp, parts, "/")
    day = parts[1]
    month = parts[2]
    year_hour = parts[3]
    split(year_hour, yh, ":")
    year = yh[1]
    date = day "/" month "/" year
    print date
}' "${LOG_FILE}" | sort | uniq -c | sort -rn | head -1 | awk '{print "  " $2 " with " $1 " requests"}'
echo ""

# Quietest day
echo "Quietest Day:"
awk '{
    # Extract timestamp between [ and ]
    start = index($0, "[") + 1
    end = index($0, "]") - 1
    timestamp = substr($0, start, end - start + 1)
    split(timestamp, parts, "/")
    day = parts[1]
    month = parts[2]
    year_hour = parts[3]
    split(year_hour, yh, ":")
    year = yh[1]
    date = day "/" month "/" year
    print date
}' "${LOG_FILE}" | sort | uniq -c | sort -n | head -1 | awk '{print "  " $2 " with " $1 " requests"}'
echo ""

# Advanced Analysis

echo "Advanced Analysis"
echo ""

# Response size analysis
echo "Response Size:"
total_bytes=$(awk '{sum += $10} END {print sum}' "${LOG_FILE}")
avg_bytes=$(awk "BEGIN {printf \"%.0f\", $total_bytes / $total_requests}")
max_bytes=$(awk '{print $10}' "${LOG_FILE}" | sort -rn | head -1)
echo "  Average response size: ${avg_bytes} bytes"
echo "  Maximum response size: ${max_bytes} bytes"
echo ""

# Find largest response with details
echo "Largest Response Details:"
awk '{print $10, $0}' "${LOG_FILE}" | sort -rn | head -1 | awk '{
    bytes = $1
    $1 = ""
    request_line = $0
    print "  Bytes: " bytes
    print "  Request:" request_line
}'
echo ""

# Hurricane outage detection (simplified)
echo "Hurricane Outage Analysis:"
first_entry=$(head -1 "${LOG_FILE}" | awk '{start = index($0, "[") + 1; end = index($0, "]") - 1; print substr($0, start, end - start + 1)}')
last_entry=$(tail -1 "${LOG_FILE}" | awk '{start = index($0, "[") + 1; end = index($0, "]") - 1; print substr($0, start, end - start + 1)}')
echo "  Log file spans from: $first_entry"
echo "  To: $last_entry"
echo "  (For August data, look for gaps indicating hurricane outage periods)"
echo ""

# Error patterns
echo "Error Patterns (by HTTP status code):"
awk '$9 >= 400' "${LOG_FILE}" | awk '{print $9}' | sort | uniq -c | sort -rn | awk '{
    print "  Code " $2 ": " $1 " errors"
}'
echo ""

echo "Error Patterns (by hour of day):"
awk '$9 >= 400' "${LOG_FILE}" | awk '{
    # Extract timestamp between [ and ]
    start = index($0, "[") + 1
    end = index($0, "]") - 1
    timestamp = substr($0, start, end - start + 1)
    split(timestamp, parts, ":")
    hour = parts[2]
    print hour
}' | sort | uniq -c | sort -rn | awk '{
    printf "  %s:00 - %s errors\n", $2, $1
}'
echo ""

echo "Top Hosts with Most Errors:"
awk '$9 >= 400' "${LOG_FILE}" | awk '{print $1}' | sort | uniq -c | sort -rn | head -5 | awk '{print "  " $2 " (" $1 " errors)"}'
echo ""

echo "Analysis Complete"
