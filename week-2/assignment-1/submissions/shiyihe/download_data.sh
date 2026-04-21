#!/bin/bash

set -euo pipefail

LOG_FILE="logs/download.log"
DATA_DIR="data"
BACKUP_DIR="backup"

mkdir -p "$DATA_DIR" "$BACKUP_DIR" "logs"

echo "[$(date)] Starting download process..." | tee -a "$LOG_FILE"

cd "$DATA_DIR"

echo "[$(date)] Downloading NASA_Jul95.log..." | tee -a "../$LOG_FILE"
curl -O https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log

echo "[$(date)] Downloading NASA_Aug95.log..." | tee -a "../$LOG_FILE"
curl -O https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log

echo "[$(date)] Validating files..." | tee -a "../$LOG_FILE"
wc -l NASA_Jul95.log | tee -a "../$LOG_FILE"
wc -l NASA_Aug95.log | tee -a "../$LOG_FILE"

echo "[$(date)] Creating backups..." | tee -a "../$LOG_FILE"
cp NASA_Jul95.log ../$BACKUP_DIR/NASA_Jul95.log.bak
cp NASA_Aug95.log ../$BACKUP_DIR/NASA_Aug95.log.bak

echo "[$(date)] Download process completed successfully." | tee -a "../$LOG_FILE"

