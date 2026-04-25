#!/bin/bash
# run_pipeline.sh - Run download, then analyze, then report.

set -eu

HERE="$(cd "$(dirname "$0")" && pwd)"
DATA_DIR="${DATA_DIR:-$HERE/data}"
OUT_DIR="${OUTPUT_DIR:-$HERE/output}"

mkdir -p "$DATA_DIR"
mkdir -p "$OUT_DIR"

echo "=== Step 1: download ==="
"$HERE/download_data.sh" "$DATA_DIR"

echo "=== Step 2: analyze ==="
OUTPUT_DIR="$OUT_DIR" "$HERE/analyze_logs.sh" \
  "$DATA_DIR/NASA_Jul95.log" \
  "$DATA_DIR/NASA_Aug95.log"

echo "=== Step 3: report ==="
OUTPUT_DIR="$OUT_DIR" REPORT="$HERE/REPORT.md" "$HERE/generate_report.sh"

rm -f "$OUT_DIR/"*_minutes_sorted.txt \
      "$OUT_DIR/"*_outage_gap.txt \
      "$OUT_DIR/"*_excluded_days.txt \
      2>/dev/null || true

echo "Done. Open $HERE/REPORT.md"
