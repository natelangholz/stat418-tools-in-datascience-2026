# Permission: chmod +x analyze_logs.sh
# To run: bash analyze_logs.sh

#!/bin/bash
set -uo pipefail
export LC_ALL=C

RESULTS_FILE="analysis_results.txt"
JUL_LOG="NASA_Jul95.log"
AUG_LOG="NASA_Aug95.log"

printf -- "--- NASA Log Analysis Results ---\n" | tee "$RESULTS_FILE"

for LOG in "$JUL_LOG" "$AUG_LOG"; do
    if [ ! -f "$LOG" ]; then continue; fi

    printf -- "\n==========================================\n" | tee -a "$RESULTS_FILE"
    printf -- "Processing %s...\n" "$LOG" | tee -a "$RESULTS_FILE"
    printf -- "==========================================\n" | tee -a "$RESULTS_FILE"

    # --- BASIC ANALYSIS ---
    printf -- "\n[BASIC ANALYSIS]\n" | tee -a "$RESULTS_FILE"
    
    printf -- "1. Top 10 Hosts (Excluding 404s):\n" | tee -a "$RESULTS_FILE"
    awk '$9 != "404" {count[$1]++} END {for (i in count) print count[i], i}' "$LOG" | sort -rn | head -n 10 | tee -a "$RESULTS_FILE"

    printf -- "2. IP vs Hostname Percentage:\n" | tee -a "$RESULTS_FILE"
    awk '{if ($1 ~ /^[0-9]+\.[0-9]/) ip++; else host++} END {if (NR > 0) printf "IPs: %.2f%% | Hostnames: %.2f%%\n", (ip/NR)*100, (host/NR)*100; else print "No data."}' "$LOG" | tee -a "$RESULTS_FILE"

    printf -- "3. Top 10 Requests (Excluding 404s):\n" | tee -a "$RESULTS_FILE"
    awk '$9 != "404" {count[$7]++} END {for (i in count) print count[i], i}' "$LOG" | sort -rn | head -n 10 | tee -a "$RESULTS_FILE"

    printf -- "4. Request Types (Methods):\n" | tee -a "$RESULTS_FILE"
    awk '{split($6, a, "\""); if (a[2] ~ /^(GET|POST|HEAD)$/) count[a[2]]++} END {for (m in count) print count[m], m}' "$LOG" | sort -rn | tee -a "$RESULTS_FILE"

    printf -- "5. Total 404 Errors:\n" | tee -a "$RESULTS_FILE"
    awk '$9 == "404" {count++} END {print count+0}' "$LOG" | tee -a "$RESULTS_FILE"

    printf -- "6. Most Frequent Response Code:\n" | tee -a "$RESULTS_FILE"
    awk '{if($9 ~ /^[0-9]+$/) {count[$9]++; total++}} END {if (total > 0) for (c in count) print count[c], c, total}' "$LOG" | sort -rn | head -n 1 | awk '{printf "Code %s (%.2f%%)\n", $2, ($1/$3)*100}' | tee -a "$RESULTS_FILE"

    # --- TIME-BASED ANALYSIS ---
    printf -- "\n[TIME-BASED ANALYSIS]\n" | tee -a "$RESULTS_FILE"

    printf -- "7. Peak and Quiet Hours:\n" | tee -a "$RESULTS_FILE"
    awk '{ match($0, /:[0-9]{2}:[0-9]{2}:[0-9]{2}/); if (RSTART>0) { hour=substr($0, RSTART+1, 2); count[hour]++ } } 
         END { for (h in count) print count[h], h":00" }' "$LOG" | sort -n | \
         awk 'NR>0 {p_val=$1; p_hr=$2} NR==1{q_val=$1; q_hr=$2} 
         END {if (NR>0) {print "Peak: " p_hr " (" p_val " reqs)"; print "Quiet: " q_hr " (" q_val " reqs)"} else print "No data."}' | tee -a "$RESULTS_FILE"

    printf -- "8. Busiest Day:\n" | tee -a "$RESULTS_FILE"
    awk -F'[' '{split($2, a, ":"); if(a[1] != "") count[a[1]]++} END {for (d in count) print count[d], d}' "$LOG" | sort -rn | head -n 1 | tee -a "$RESULTS_FILE"

    printf -- "9. Quietest Day:\n" | tee -a "$RESULTS_FILE"
    if [[ "$LOG" == "$AUG_LOG" ]]; then
        awk -F'[' '{split($2, a, ":"); if(a[1] != "" && a[1] !~ /0[123]\/Aug/) count[a[1]]++} END {for (d in count) print count[d], d}' "$LOG" | sort -n | head -n 1 | tee -a "$RESULTS_FILE"
    else
        awk -F'[' '{split($2, a, ":"); if(a[1] != "") count[a[1]]++} END {for (d in count) print count[d], d}' "$LOG" | sort -n | head -n 1 | tee -a "$RESULTS_FILE"
    fi

    # --- ADVANCED ANALYSIS ---
    printf -- "\n[ADVANCED ANALYSIS]\n" | tee -a "$RESULTS_FILE"

    printf -- "10. Max and Average Response Size:\n" | tee -a "$RESULTS_FILE"
    awk '$10 ~ /^[0-9]+$/ {sum+=$10; count++; if($10>max) max=$10} END {if (count > 0) printf "Max: %d bytes | Avg: %.2f bytes\n", max, sum/count; else print "Max: 0 bytes | Avg: 0.00 bytes"}' "$LOG" | tee -a "$RESULTS_FILE"

    printf -- "11. Error Patterns (4xx and 5xx Codes):\n" | tee -a "$RESULTS_FILE"
    printf -- "  - Top 3 Hours for Errors:\n" | tee -a "$RESULTS_FILE"
    awk '$9 >= 400 { match($0, /:[0-9]{2}:[0-9]{2}:[0-9]{2}/); if (RSTART>0) { h=substr($0, RSTART+1, 2); count[h]++ } } 
         END {for (h in count) print count[h], h":00"}' "$LOG" | sort -rn | head -n 3 | awk '{print "    " $2 " (" $1 " errors)"}' | tee -a "$RESULTS_FILE"
    
    printf -- "  - Top 3 Hosts producing Errors:\n" | tee -a "$RESULTS_FILE"
    awk '$9 >= 400 {count[$1]++} END {for (h in count) print count[h], h}' "$LOG" | sort -rn | head -n 3 | awk '{print "    " $2 " (" $1 " errors)"}' | tee -a "$RESULTS_FILE"

    if [[ "$LOG" == "$AUG_LOG" ]]; then
        printf -- "\n12. Hurricane Outage Analysis:\n" | tee -a "$RESULTS_FILE"
        
        LAST=$(grep "01/Aug/1995" "$LOG" | tail -n 1 || true)
        FIRST=$(grep "03/Aug/1995" "$LOG" | head -n 1 || true)

        if [[ -n "$LAST" && -n "$FIRST" ]]; then
            STOP_TS=$(echo "$LAST" | grep -oE "[0-9]{2}/[A-Z][a-z]{2}/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2}" || true)
            START_TS=$(echo "$FIRST" | grep -oE "[0-9]{2}/[A-Z][a-z]{2}/[0-9]{4}:[0-9]{2}:[0-9]{2}:[0-9]{2}" || true)

            # Check if timestamps were actually extracted to prevent date command crash
            if [[ -n "$STOP_TS" && -n "$START_TS" ]]; then
                if date --version >/dev/null 2>&1; then
                    STOP_SEC=$(date -d "${STOP_TS/:/ }" +%s)
                    START_SEC=$(date -d "${START_TS/:/ }" +%s)
                else
                    STOP_SEC=$(date -j -f "%d/%b/%Y:%H:%M:%S" "$STOP_TS" "+%s")
                    START_SEC=$(date -j -f "%d/%b/%Y:%H:%M:%S" "$START_TS" "+%s")
                fi

                DIFF_SEC=$((START_SEC - STOP_SEC))
                HOURS=$((DIFF_SEC / 3600))
                MINS=$(((DIFF_SEC % 3600) / 60))

                # Using -- here because $LAST and $FIRST are raw log lines
                printf -- "Data collection stopped: %s\n" "$LAST" | tee -a "$RESULTS_FILE"
                printf -- "Data collection resumed: %s\n" "$FIRST" | tee -a "$RESULTS_FILE"
                printf -- "Duration: %d hours and %d minutes (%d total seconds).\n" "$HOURS" "$MINS" "$DIFF_SEC" | tee -a "$RESULTS_FILE"
            fi
        fi
    fi
done