#!/bin/bash
# run_pipeline.sh - Master script to run the complete NASA log analysis pipeline
# Orchestrates: download_data.sh -> analyze_logs.sh -> generate_report.sh
# With error handling, progress updates, and cleanup

set -e

# Configuration
PIPELINE_LOG="pipeline_run_$(date +%Y%m%d_%H%M%S).log"
TEMP_FILES=()
START_TIME=$(date +%s)
SUCCESS=0
FAILED=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_message() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message" | tee -a "$PIPELINE_LOG"
            ;;
        SUCCESS)
            echo -e "${GREEN}[✓ SUCCESS]${NC} $message" | tee -a "$PIPELINE_LOG"
            ;;
        ERROR)
            echo -e "${RED}[✗ ERROR]${NC} $message" | tee -a "$PIPELINE_LOG"
            ;;
        WARN)
            echo -e "${YELLOW}[⚠ WARNING]${NC} $message" | tee -a "$PIPELINE_LOG"
            ;;
        PROGRESS)
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$PIPELINE_LOG"
            echo -e "${BLUE}▶ $message${NC}" | tee -a "$PIPELINE_LOG"
            echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$PIPELINE_LOG"
            ;;
    esac
}

cleanup() {
    local exit_code=$?
    
    log_message INFO "Cleaning up temporary files..."
    
    # Remove analysis cache files if cleanup is enabled
    if [[ "${CLEANUP_ANALYSIS:-1}" == "1" ]]; then
        rm -f NASA_Jul95_analysis.txt NASA_Aug95_analysis.txt
        log_message SUCCESS "Cleaned up analysis cache files"
    fi
    
    # Calculate elapsed time
    local end_time=$(date +%s)
    local elapsed=$((end_time - START_TIME))
    local minutes=$((elapsed / 60))
    local seconds=$((elapsed % 60))
    
    # Print final summary
    echo "" | tee -a "$PIPELINE_LOG"
    log_message PROGRESS "PIPELINE EXECUTION COMPLETE"
    
    if [[ $exit_code -eq 0 ]]; then
        log_message SUCCESS "All stages completed successfully"
        log_message INFO "Total execution time: ${minutes}m ${seconds}s"
        log_message INFO "Output files:"
        log_message INFO "  - NASA_Jul95.log (July web server log)"
        log_message INFO "  - NASA_Aug95.log (August web server log)"
        log_message INFO "  - NASA_WebServer_Analysis_Report.md (Comprehensive analysis report)"
        log_message INFO "  - $PIPELINE_LOG (Pipeline execution log)"
    else
        log_message ERROR "Pipeline failed at one or more stages (exit code: $exit_code)"
        log_message INFO "Check $PIPELINE_LOG for details"
    fi
    
    echo "" | tee -a "$PIPELINE_LOG"
}

error_handler() {
    local line_number=$1
    local error_code=$2
    log_message ERROR "Error occurred in pipeline at line $line_number (exit code: $error_code)"
    exit $error_code
}

# Set up error handling and cleanup
trap cleanup EXIT
trap 'error_handler ${LINENO} $?' ERR

# Main pipeline execution
main() {
    echo ""
    log_message PROGRESS "NASA WEB SERVER LOG ANALYSIS PIPELINE"
    log_message INFO "Start time: $(date '+%Y-%m-%d %H:%M:%S')"
    log_message INFO "Log file: $PIPELINE_LOG"
    echo ""
    
    # ============================================================================
    # STAGE 1: Download Data
    # ============================================================================
    log_message PROGRESS "STAGE 1: DOWNLOADING WEB SERVER LOGS"
    
    if [[ ! -f download_data.sh ]]; then
        log_message ERROR "download_data.sh not found"
        return 1
    fi
    
    if [[ ! -x download_data.sh ]]; then
        log_message WARN "download_data.sh is not executable, making it executable..."
        chmod +x download_data.sh
    fi
    
    log_message INFO "Running download_data.sh..."
    
    if ./download_data.sh >> "$PIPELINE_LOG" 2>&1; then
        if [[ -f NASA_Jul95.log ]] && [[ -f NASA_Aug95.log ]]; then
            local jul_size=$(du -h NASA_Jul95.log | cut -f1)
            local aug_size=$(du -h NASA_Aug95.log | cut -f1)
            local jul_lines=$(wc -l < NASA_Jul95.log)
            local aug_lines=$(wc -l < NASA_Aug95.log)
            
            log_message SUCCESS "Downloaded both log files"
            log_message INFO "  - NASA_Jul95.log: $jul_size ($jul_lines lines)"
            log_message INFO "  - NASA_Aug95.log: $aug_size ($aug_lines lines)"
        else
            log_message ERROR "Log files not found after download"
            return 1
        fi
    else
        log_message ERROR "download_data.sh failed"
        return 1
    fi
    
    echo "" | tee -a "$PIPELINE_LOG"
    
    # ============================================================================
    # STAGE 2: Analyze Logs
    # ============================================================================
    log_message PROGRESS "STAGE 2: ANALYZING WEB SERVER LOGS"
    
    if [[ ! -f analyze_logs.sh ]]; then
        log_message ERROR "analyze_logs.sh not found"
        return 1
    fi
    
    if [[ ! -x analyze_logs.sh ]]; then
        log_message WARN "analyze_logs.sh is not executable, making it executable..."
        chmod +x analyze_logs.sh
    fi
    
    log_message INFO "Analyzing July log (1.8M+ lines - this may take a few minutes)..."
    if ./analyze_logs.sh NASA_Jul95.log > NASA_Jul95_analysis.txt 2>&1; then
        local jul_analysis_lines=$(wc -l < NASA_Jul95_analysis.txt)
        log_message SUCCESS "July analysis complete ($jul_analysis_lines lines)"
    else
        log_message ERROR "July analysis failed"
        return 1
    fi
    
    log_message INFO "Analyzing August log (1.5M+ lines - this may take a few minutes)..."
    if ./analyze_logs.sh NASA_Aug95.log > NASA_Aug95_analysis.txt 2>&1; then
        local aug_analysis_lines=$(wc -l < NASA_Aug95_analysis.txt)
        log_message SUCCESS "August analysis complete ($aug_analysis_lines lines)"
    else
        log_message ERROR "August analysis failed"
        return 1
    fi
    
    echo "" | tee -a "$PIPELINE_LOG"
    
    # ============================================================================
    # STAGE 3: Generate Report
    # ============================================================================
    log_message PROGRESS "STAGE 3: GENERATING COMPREHENSIVE REPORT"
    
    if [[ ! -f generate_report.sh ]]; then
        log_message ERROR "generate_report.sh not found"
        return 1
    fi
    
    if [[ ! -x generate_report.sh ]]; then
        log_message WARN "generate_report.sh is not executable, making it executable..."
        chmod +x generate_report.sh
    fi
    
    log_message INFO "Generating markdown report..."
    if ./generate_report.sh NASA_Jul95.log NASA_Aug95.log >> "$PIPELINE_LOG" 2>&1; then
        if [[ -f NASA_WebServer_Analysis_Report.md ]]; then
            local report_lines=$(wc -l < NASA_WebServer_Analysis_Report.md)
            local report_size=$(du -h NASA_WebServer_Analysis_Report.md | cut -f1)
            
            log_message SUCCESS "Report generated successfully"
            log_message INFO "  - NASA_WebServer_Analysis_Report.md: $report_size ($report_lines lines)"
        else
            log_message ERROR "Report file not found after generation"
            return 1
        fi
    else
        log_message ERROR "Report generation failed"
        return 1
    fi
    
    echo "" | tee -a "$PIPELINE_LOG"
    
    # ============================================================================
    # STAGE 4: Verification and Summary
    # ============================================================================
    log_message PROGRESS "STAGE 4: VERIFICATION AND SUMMARY"
    
    log_message INFO "Verifying all output files..."
    
    local all_files_exist=1
    
    if [[ ! -f NASA_Jul95.log ]]; then
        log_message ERROR "NASA_Jul95.log not found"
        all_files_exist=0
    else
        log_message SUCCESS "✓ NASA_Jul95.log"
    fi
    
    if [[ ! -f NASA_Aug95.log ]]; then
        log_message ERROR "NASA_Aug95.log not found"
        all_files_exist=0
    else
        log_message SUCCESS "✓ NASA_Aug95.log"
    fi
    
    if [[ ! -f NASA_WebServer_Analysis_Report.md ]]; then
        log_message ERROR "NASA_WebServer_Analysis_Report.md not found"
        all_files_exist=0
    else
        log_message SUCCESS "✓ NASA_WebServer_Analysis_Report.md"
    fi
    
    if [[ ! -f download.log ]]; then
        log_message WARN "download.log not found"
    else
        log_message SUCCESS "✓ download.log (download operation log)"
    fi
    
    if [[ $all_files_exist -eq 0 ]]; then
        log_message ERROR "Some required files are missing"
        return 1
    fi
    
    # Print summary statistics
    echo "" | tee -a "$PIPELINE_LOG"
    log_message INFO "PIPELINE SUMMARY:"
    
    local jul_lines=$(wc -l < NASA_Jul95.log)
    local aug_lines=$(wc -l < NASA_Aug95.log)
    local jul_size=$(du -h NASA_Jul95.log | cut -f1)
    local aug_size=$(du -h NASA_Aug95.log | cut -f1)
    
    echo "" | tee -a "$PIPELINE_LOG"
    echo "📊 DATA DOWNLOADED:" | tee -a "$PIPELINE_LOG"
    echo "  July 1995:   $jul_lines requests ($jul_size)" | tee -a "$PIPELINE_LOG"
    echo "  August 1995: $aug_lines requests ($aug_size)" | tee -a "$PIPELINE_LOG"
    echo "  Total:       $((jul_lines + aug_lines)) requests combined" | tee -a "$PIPELINE_LOG"
    echo "" | tee -a "$PIPELINE_LOG"
    
    echo "📈 ANALYSIS GENERATED:" | tee -a "$PIPELINE_LOG"
    echo "  - Top hosts and request patterns identified" | tee -a "$PIPELINE_LOG"
    echo "  - Response codes and error rates analyzed" | tee -a "$PIPELINE_LOG"
    echo "  - Time-based traffic patterns studied" | tee -a "$PIPELINE_LOG"
    echo "  - Response size statistics calculated" | tee -a "$PIPELINE_LOG"
    echo "" | tee -a "$PIPELINE_LOG"
    
    echo "📄 REPORT GENERATED:" | tee -a "$PIPELINE_LOG"
    echo "  - Comprehensive markdown report with findings" | tee -a "$PIPELINE_LOG"
    echo "  - July vs August comparative analysis" | tee -a "$PIPELINE_LOG"
    echo "  - ASCII visualizations of trends" | tee -a "$PIPELINE_LOG"
    echo "  - Key anomalies and recommendations" | tee -a "$PIPELINE_LOG"
    echo "  - Historical context and conclusions" | tee -a "$PIPELINE_LOG"
    echo "" | tee -a "$PIPELINE_LOG"
    
    return 0
}

# Display usage
show_usage() {
    cat << 'USAGE'
NASA WebServer Log Analysis Pipeline
======================================

Usage: ./run_pipeline.sh [OPTIONS]

OPTIONS:
    -h, --help              Show this help message
    -k, --keep-cache        Keep analysis cache files (default: clean up)
    -v, --verbose           Enable verbose output

DESCRIPTION:
    This script orchestrates the complete NASA log analysis pipeline:
    1. Downloads July and August 1995 web server logs
    2. Analyzes logs for patterns and statistics
    3. Generates comprehensive markdown report
    4. Provides progress updates and error handling

OUTPUT FILES:
    - NASA_Jul95.log                 July web server log
    - NASA_Aug95.log                 August web server log
    - NASA_WebServer_Analysis_Report.md  Comprehensive analysis report
    - pipeline_run_*.log             Pipeline execution log
    - download.log                   Download operation log

EXAMPLES:
    ./run_pipeline.sh                Run full pipeline with cleanup
    ./run_pipeline.sh --keep-cache   Run pipeline and keep cache files
    ./run_pipeline.sh -v             Run with verbose output

REQUIREMENTS:
    - download_data.sh (must be in same directory)
    - analyze_logs.sh (must be in same directory)
    - generate_report.sh (must be in same directory)
    - Internet connection for downloading logs
    - bash 4.0+
    - Standard Unix utilities (awk, sort, grep, etc.)

TIME ESTIMATE:
    - Download: 5-15 minutes (depending on connection)
    - Analysis: 10-20 minutes (for ~1.9M and ~1.6M requests)
    - Report generation: < 1 minute
    - Total: 20-40 minutes

USAGE
}

# Parse command line arguments
CLEANUP_ANALYSIS=1
VERBOSE=0

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -k|--keep-cache)
            CLEANUP_ANALYSIS=0
            log_message INFO "Cache files will be kept after completion"
            shift
            ;;
        -v|--verbose)
            VERBOSE=1
            shift
            ;;
        *)
            log_message ERROR "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Run main pipeline
main
