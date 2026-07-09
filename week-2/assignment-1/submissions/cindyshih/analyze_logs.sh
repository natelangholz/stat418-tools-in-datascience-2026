#!/bin/bash
set -u
export LC_ALL=C

# Directories for input data and output analysis
DATA_DIR="data"
ANALYSIS_DIR="analysis"

mkdir -p "$ANALYSIS_DIR"

# Function to analyze a single log file and generate a report
# Parameters:
#   $1: input_file - path to the log file
#   $2: output_file - path to the output analysis file
#   $3: month_name - descriptive name for the month (e.g., "July 1995")
analyze_log() {
  local input_file="$1"
  local output_file="$2"
  local month_name="$3"

  if [[ ! -f "$input_file" ]]; then
    echo "ERROR: File not found: $input_file"
    return 1
  fi

  {
    echo "=========================================="
    echo "NASA Log Analysis - $month_name"
    echo "File: $input_file"
    echo "=========================================="
    echo

    echo "BASIC ANALYSIS"
    echo "--------------"

    # 1. Top 10 hosts/IPs making requests, excluding 404 errors
    echo "1. Top 10 hosts/IPs making requests (excluding 404 errors):"
    awk '$9 != 404 {print $1}' "$input_file" | sort | uniq -c | sort -nr | head -10
    echo

    # 2. Percentage breakdown of requests from IP addresses vs hostnames
    echo "2. Percentage of requests from IP addresses vs hostnames:"
    awk '
    {
      total++
      if ($1 ~ /^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$/)
        ip++
      else
        host++
    }
    END {
      printf("IP addresses: %.2f%% (%d)\n", (ip/total)*100, ip)
      printf("Hostnames: %.2f%% (%d)\n", (host/total)*100, host)
    }' "$input_file"
    echo

    # 3. Top 10 most requested URLs, excluding 404 errors
    echo "3. Top 10 most requested URLs (excluding 404 errors):"
    awk -F'"' '
    {
    split($2, req, " ")
    split($3, right, " ")
    
    url = req[2]
    code = right[1]
    
    if (url ~ /^\// && code != 404)
    print url
    }' "$input_file" | sort | uniq -c | sort -nr | head -10
    echo

    # 4. Count of each HTTP request method
    echo "4. HTTP request methods with counts:"
    awk '
    NF >= 10 && $6 ~ /^"(GET|POST|HEAD|PUT|DELETE|OPTIONS)$/{
      gsub(/"/, "", $6)
      print $6
    }' "$input_file" | sort | uniq -c | sort -nr
    echo

    # 5. Total number of 404 errors
    echo "5. Number of 404 errors:"
    awk '
    NF >= 10 && $9 == 404 { count++ }
    END { print count + 0 }
    ' "$input_file"
    echo
   
    # 6. Most frequent HTTP response code and its percentage
    echo "6. Most frequent response code and percentage:"
    awk '
    {
      code[$9]++
      total++
    }
    END {
      max_code = ""
      max_count = 0
      for (c in code) {
        if (code[c] > max_count) {
          max_count = code[c]
          max_code = c
        }
      }
      printf("Most frequent response code: %s\n", max_code)
      printf("Count: %d\n", max_count)
      printf("Percentage: %.2f%%\n", (max_count/total)*100)
    }' "$input_file"
    echo

    echo "TIME-BASED ANALYSIS"
    echo "-------------------"

    # 7. Hour(s) with the most requests (Peak hours)
    echo "7. Peak hour(s):"
    awk '
    {
      split($4, a, ":")
      hour = a[2]
      hour_count[hour]++
    }
    END {
      max = 0
      for (h in hour_count) {
        if (hour_count[h] > max)
          max = hour_count[h]
      }
      for (h in hour_count) {
        if (hour_count[h] == max)
          printf("%s:00 with %d requests\n", h, hour_count[h])
      }
    }' "$input_file"
    echo

    # 7. Hour(s) with the least requests (Quiet hours)
    echo "Quietest hour(s):"
    awk '
    NF >= 4 && $4 ~ /^\[[0-9]{2}\/[A-Za-z]{3}\/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2}$/{
      split($4, a, ":")
      hour = a[2]
      hour_count[hour]++
    }
    END {
      min = -1
      for (h in hour_count) {
        if (min == -1 || hour_count[h] < min)
          min = hour_count[h]
      }
      for (h in hour_count) {
        if (hour_count[h] == min)
          printf("%s:00 with %d requests\n", h, hour_count[h])
      }
    }' "$input_file"
    echo

    # 8. Day with the most requests
    echo "8. Busiest day:"
    awk '
    {
      split($4, a, ":")
      day = a[1]
      gsub(/\[/, "", day)
      day_count[day]++
    }
    END {
      max_day = ""
      max_count = 0
      for (d in day_count) {
        if (day_count[d] > max_count) {
          max_count = day_count[d]
          max_day = d
        }
      }
      printf("%s with %d requests\n", max_day, max_count)
    }' "$input_file"
    echo

    # 9. Day with the least requests, excluding outage dates for August
    echo "9. Quietest day (excluding outage dates if applicable):"
    if [[ "$month_name" == "August 1995" ]]; then
      awk '
      NF >= 4 && $4 ~ /^\[[0-9]{2}\/[A-Za-z]{3}\/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2}$/{
        split($4, a, ":")
        day = a[1]
        gsub(/\[/, "", day)
        day_count[day]++
      }
      END {
        min_day = ""
        min_count = -1
        for (d in day_count) {
          # exclude suspected outage dates in August
          if (d != "04/Aug/1995" && d != "05/Aug/1995") {
            if (min_count == -1 || day_count[d] < min_count) {
              min_count = day_count[d]
              min_day = d
            }
          }
        }
        printf("%s with %d requests\n", min_day, min_count)
      }' "$input_file"
    else
      awk '
      NF >= 4 && $4 ~ /^\[[0-9]{2}\/[A-Za-z]{3}\/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2}$/{
        split($4, a, ":")
        day = a[1]
        gsub(/\[/, "", day)
        day_count[day]++
      }
      END {
        min_day = ""
        min_count = -1
        for (d in day_count) {
          if (min_count == -1 || day_count[d] < min_count) {
            min_count = day_count[d]
            min_day = d
          }
        }
        printf("%s with %d requests\n", min_day, min_count)
      }' "$input_file"
    fi
    echo

    echo "ADVANCED ANALYSIS"
    echo "-----------------"

    # 10. Detect hurricane outage in August by finding the largest gap in timestamps
    if [[ "$month_name" == "August 1995" ]]; then
      echo "10. Hurricane outage (largest gap in log timestamps):"
      awk '
      function to_seconds(day, hour, min, sec) {
        return (((day * 24) + hour) * 60 + min) * 60 + sec
      }
      {
        raw = $4
        gsub(/\[/, "", raw)
        split(raw, a, /[\/:]/)

        day = a[1]
        hour = a[4]
        min = a[5]
        sec = a[6]

        current_time = to_seconds(day, hour, min, sec)

        if (NR > 1) {
          gap = current_time - previous_time
          if (gap > max_gap) {
            max_gap = gap
            start_stamp = previous_stamp
            end_stamp = raw
          }
        }

        previous_time = current_time
        previous_stamp = raw
      }
      END {
        hours = int(max_gap / 3600)
        minutes = int((max_gap % 3600) / 60)
        seconds = max_gap % 60

        print "Last entry before outage: " start_stamp
        print "First entry after outage: " end_stamp
        printf("Outage duration: %d seconds (%d hours, %d minutes, %d seconds)\n", max_gap, hours, minutes, seconds)
      }' "$input_file"
    else
      echo "10. Hurricane outage: Not applicable for July log"
    fi
    echo

    # 11. Analysis of response sizes: largest and average
    echo "11. Response size analysis:"
    awk '
    $10 ~ /^[0-9]+$/ {
      total_size += $10
      count++
      if ($10 > max_size)
        max_size = $10
    }
    END {
      printf("Largest response size: %d bytes\n", max_size)
      printf("Average response size: %.2f bytes\n", total_size / count)
    }' "$input_file"
    echo

    # 12. Patterns in errors: by hour and top error-causing hosts
    echo "12. Error patterns:"
    echo "Errors by hour (4xx and 5xx):"
    awk '
    NF >= 10 && $9 >= 400 && $9 < 600 {
      split($4, a, ":")
      hour = a[2]
      error_hour[hour]++
    }
    END {
      for (h in error_hour)
      printf "%d %s:00\n", error_hour[h], h
    }' "$input_file" | sort -nr
    echo

    echo "Top hosts causing errors:"
    awk '$9 >= 400 && $9 < 600 {print $1}' "$input_file" | sort | uniq -c | sort -nr | head -10
    echo

  } > "$output_file"

  echo "Finished analysis for $month_name -> $output_file"
}

# Main script execution
echo "Starting log analysis..."

# Analyze July 1995 log
analyze_log "$DATA_DIR/NASA_Jul95.log" "$ANALYSIS_DIR/july_analysis.txt" "July 1995"

# Analyze August 1995 log
analyze_log "$DATA_DIR/NASA_Aug95.log" "$ANALYSIS_DIR/august_analysis.txt" "August 1995"

echo "Analysis complete!"