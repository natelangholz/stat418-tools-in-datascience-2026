#!/bin/bash
# hw1-starter.sh - Download NASA log files

# Part 4: Handle errors gracefully
set -euo pipefail
# -e: exit immediately if a command fails
# -u: treat unset variables as an error
# -o pipefail: return the exit status of the last command in the pipeline that failed

# Part 5: File for Log operations with timestamps
operations_file="operations_log.txt"

# Part 1: Downloads both log files
echo "Downloading NASA web server logs..."

# Download July log
curl -s https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log > NASA_Jul95.log
echo "Downloaded NASA_Jul95.log"
echo "[$(ls -lh NASA_Jul95.log | awk '{print $8}')] Downloaded NASA_Jul95.log" >> "$operations_file"

# Download August log
curl -s https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log > NASA_Aug95.log
echo "Downloaded NASA_Aug95.log"
echo "[$(ls -lh NASA_Aug95.log | awk '{print $8}')] Downloaded NASA_Aug95.log" >> "$operations_file"

echo "Download complete!"
echo "[$(date | awk '{print $4}')] Download complete!" >> "$operations_file"

# Part 2: Validates Downloads

# part a: file size check
echo "NASA_Jul95.log file size:"
ls -lh NASA_Jul95.log

echo "NASA_Aug95.log file size:"
ls -lh NASA_Aug95.log

# part b: line count check
echo "NASA_Jul95.log line count:"
wc -l NASA_Jul95.log

echo "NASA_Aug95.log line count:"
wc -l NASA_Aug95.log

echo "[$(date | awk '{print $4}')] Validation complete!" >> "$operations_file"

# Part 3: Create a backup of the original files
cp NASA_Jul95.log backup_NASA_Jul95.log
echo "[$(ls -lh backup_NASA_Jul95.log | awk '{print $8}')] Created back up of NASA_Jul95.log" >> "$operations_file"
cp NASA_Aug95.log backup_NASA_Aug95.log
echo "[$(ls -lh backup_NASA_Aug95.log | awk '{print $8}')] Created back up of NASA_Aug95.log" >> "$operations_file"





