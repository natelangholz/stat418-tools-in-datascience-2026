#!/usr/bin/env bash
# run_pipeline.sh
# -----------------------------------------------------------------------------
# Part 4: Pipeline Integration
#
# Master driver: downloads data → analyzes July → analyzes August →
# generates REPORT.md → cleans up intermediate files.
#
# The script is idempotent: re-running it after a successful download skips
# the download step (download_data.sh checks for a valid existing file).
#
# Usage:
#   ./run_pipeline.sh                 # default WORKDIR=./work, REPORT=./REPORT.md
#   ./run_pipeline.sh ./work REPORT.md
# -----------------------------------------------------------------------------

set -euo pipefail

# --- Config ------------------------------------------------------------------
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly WORKDIR="${1:-${SCRIPT_DIR}/work}"
readonly REPORT="${2:-${SCRIPT_DIR}/REPORT.md}"

readonly DATA_DIR="${WORKDIR}/data"
readonly JUL_OUT="${WORKDIR}/jul"
readonly AUG_OUT="${WORKDIR}/aug"
readonly RUN_LOG="${WORKDIR}/pipeline_$(date +%Y%m%d_%H%M%S).log"

# --- Logging helpers ---------------------------------------------------------
log() {
  local ts
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf "[%s] %s\n" "${ts}" "$*" | tee -a "${RUN_LOG}"
}

step() {
  echo ""
  log "========== $* =========="
}

on_error() {
  local exit_code=$?
  log "PIPELINE FAILED at line ${BASH_LINENO[0]} (exit ${exit_code})"
  log "See log at ${RUN_LOG}"
  exit "${exit_code}"
}
trap on_error ERR

# --- Setup -------------------------------------------------------------------
mkdir -p "${WORKDIR}" "${DATA_DIR}" "${JUL_OUT}" "${AUG_OUT}"
: > "${RUN_LOG}"
log "run_pipeline.sh starting"
log "WORKDIR=${WORKDIR}"
log "REPORT=${REPORT}"

# --- Step 1: Download --------------------------------------------------------
step "1/4  Downloading NASA log files"
bash "${SCRIPT_DIR}/download_data.sh" "${DATA_DIR}"

JUL_LOG="${DATA_DIR}/NASA_Jul95.log"
AUG_LOG="${DATA_DIR}/NASA_Aug95.log"
[[ -s "${JUL_LOG}" ]] || { log "July log missing or empty"; exit 1; }
[[ -s "${AUG_LOG}" ]] || { log "August log missing or empty"; exit 1; }

# --- Step 2: Analyze July ----------------------------------------------------
step "2/4  Analyzing July log"
bash "${SCRIPT_DIR}/analyze_logs.sh" "${JUL_LOG}" "${JUL_OUT}"

# --- Step 3: Analyze August --------------------------------------------------
step "3/4  Analyzing August log"
bash "${SCRIPT_DIR}/analyze_logs.sh" "${AUG_LOG}" "${AUG_OUT}"

# --- Step 4: Report ----------------------------------------------------------
step "4/4  Generating REPORT.md"
bash "${SCRIPT_DIR}/generate_report.sh" "${JUL_OUT}" "${AUG_OUT}" "${REPORT}"

# --- Cleanup -----------------------------------------------------------------
# Remove the large intermediate normalized.tsv files (easy to regenerate) but
# keep the per-question text outputs because they're small and useful to
# inspect independently of REPORT.md.
step "Cleaning up intermediate files"
rm -f "${JUL_OUT}/normalized.tsv" "${AUG_OUT}/normalized.tsv" 2>/dev/null || true
rm -f "${JUL_OUT}/_epochs.txt"    "${AUG_OUT}/_epochs.txt"    2>/dev/null || true

log "Pipeline complete."
log "Report: ${REPORT}"
log "Per-question outputs: ${JUL_OUT}/  ${AUG_OUT}/"
