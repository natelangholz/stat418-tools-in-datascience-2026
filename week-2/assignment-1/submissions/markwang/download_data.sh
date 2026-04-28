#!/bin/bash
# hw1-starter.sh - Download NASA log files with validation and backups

set -euo pipefail

LOG_FILE="download.log"

# Logging function
log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${LOG_FILE}"
}

# Create backup of existing file if it exists
backup_file() {
    local file="$1"
    
    if [[ -f "${file}" ]]; then
        local backup_timestamp=$(date '+%Y%m%d_%H%M%S')
        local backup_name="${file}.backup.${backup_timestamp}"
        cp "${file}" "${backup_name}"
        log "INFO" "Created backup: ${backup_name}"
    fi
}

# Download file with error handling and retry logic
download_file() {
    local url="$1"
    local output="$2"
    local max_retries=3
    local retry_count=0
    
    log "INFO" "Starting download: ${url}"
    
    while [[ ${retry_count} -lt ${max_retries} ]]; do
        if curl -f -L -o "${output}" "${url}" 2>/dev/null; then
            log "INFO" "Successfully downloaded: ${output}"
            return 0
        else
            retry_count=$((retry_count + 1))
            if [[ ${retry_count} -lt ${max_retries} ]]; then
                log "WARN" "Download failed (attempt ${retry_count}/${max_retries}). Retrying in 2 seconds..."
                sleep 2
            fi
        fi
    done
    
    log "ERROR" "Failed to download after ${max_retries} attempts: ${url}"
    return 1
}

# Validate file
validate_file() {
    local file="$1"
    local file_name=$(basename "${file}")
    
    if [[ ! -f "${file}" ]]; then
        log "ERROR" "File does not exist: ${file}"
        return 1
    fi
    
    # Get file size in bytes
    local file_size=$(stat -f%z "${file}" 2>/dev/null || stat -c%s "${file}" 2>/dev/null)
    log "INFO" "File size for ${file_name}: ${file_size} bytes"
    
    # Get line count
    local line_count=$(wc -l < "${file}")
    log "INFO" "Line count for ${file_name}: ${line_count} lines"
    
    # Check if file is empty
    if [[ ${file_size} -eq 0 ]]; then
        log "ERROR" "File is empty: ${file}"
        return 1
    fi
    
    if [[ ${line_count} -eq 0 ]]; then
        log "ERROR" "File has no lines: ${file}"
        return 1
    fi
    
    return 0
}

# Main execution
echo "Downloading NASA web server logs..."

# Initialize log file
if [[ ! -f "${LOG_FILE}" ]]; then
    touch "${LOG_FILE}"
fi

log "INFO" "=========================================="
log "INFO" "Download Data Script Started"
log "INFO" "=========================================="

# Download July log
backup_file "NASA_Jul95.log"
if download_file "https://atlas.cs.brown.edu/data/web-logs/NASA_Jul95.log" "NASA_Jul95.log"; then
    if validate_file "NASA_Jul95.log"; then
        echo "Downloaded NASA_Jul95.log"
    else
        log "ERROR" "Validation failed for NASA_Jul95.log"
        exit 1
    fi
else
    exit 1
fi

# Download August log
backup_file "NASA_Aug95.log"
if download_file "https://atlas.cs.brown.edu/data/web-logs/NASA_Aug95.log" "NASA_Aug95.log"; then
    if validate_file "NASA_Aug95.log"; then
        echo "Downloaded NASA_Aug95.log"
    else
        log "ERROR" "Validation failed for NASA_Aug95.log"
        exit 1
    fi
else
    exit 1
fi

log "INFO" "=========================================="
log "INFO" "Download Data Script Completed Successfully"
log "INFO" "=========================================="
echo "Download complete!"
