
set -euo pipefail

BASE_DIR="${1:-$(pwd)}"
DATA_DIR="$BASE_DIR/data"
LOG_DIR="$BASE_DIR/logs"
ANALYSIS_DIR="$BASE_DIR/analysis"
TMP_DIR="$BASE_DIR/tmp"
REPORT_FILE="$BASE_DIR/REPORT.md"

mkdir -p "$DATA_DIR" "$LOG_DIR" "$ANALYSIS_DIR" "$TMP_DIR"

say() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

say "Step 1/4: Downloading and validating data"
./download_data.sh "$DATA_DIR" "$LOG_DIR"

say "Step 2/4: Running July analysis"
./analyze_logs.sh "$DATA_DIR/NASA_Jul95.log" "$ANALYSIS_DIR"

say "Step 2/4: Running August analysis"
./analyze_logs.sh "$DATA_DIR/NASA_Aug95.log" "$ANALYSIS_DIR"

say "Step 3/4: Generating markdown report"
./generate_report.sh "$ANALYSIS_DIR" "$REPORT_FILE"

say "Step 4/4: Pipeline complete"
say "Final report: $REPORT_FILE"
