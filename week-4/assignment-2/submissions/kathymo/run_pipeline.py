"""
run_pipeline.py
---------------
Runs the full movie data pipeline in order:

  1. api_collector.py   — fetch movie metadata from the TMDB API
  2. web_scraper.py  — fetch number of fans and ratings from Letterboxd
  3. data_processor.py  — merge, clean, and validate both datasets
  4. analyze_data.py    — run analyses, generate plots, and write REPORT.md

Each step is run as a subprocess so its own logging, imports, and working
directory are fully isolated. If any step fails the pipeline stops
immediately and prints a clear error — no partial outputs are left silently.

Usage
-----
  python run_pipeline.py               # run all four steps
  python run_pipeline.py --start 3     # resume from step 3 (data_processor)
  python run_pipeline.py --only 4      # run only step 4 (analyze_data)
  python run_pipeline.py --dry-run     # print what would run, do nothing
"""

import argparse
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR  = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Logging — pipeline gets its own log alongside the per-script logs
# ---------------------------------------------------------------------------

logging.basicConfig(
    filename=str(LOG_DIR / "run_pipeline.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pipeline definition
# ---------------------------------------------------------------------------

STEPS = [
    {
        "number":      1,
        "name":        "api_collector",
        "script":      "api_collector.py",
        "description": "Fetch movie metadata from the TMDB API",
    },
    {
        "number":      2,
        "name":        "web_scraper",
        "script":      "web_scraper.py",
        "description": "Fetch number of fans & ratings from the Letterboxd",
    },
    {
        "number":      3,
        "name":        "data_processor",
        "script":      "data_processor.py",
        "description": "Merge, clean, and validate both datasets",
    },
    {
        "number":      4,
        "name":        "analyze_data",
        "script":      "analyze_data.py",
        "description": "Run analyses, generate plots, and write REPORT.md",
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _divider(char: str = "─", width: int = 58) -> str:
    return char * width


def _header(text: str) -> None:
    print(_divider("═"))
    print(f"  {text}")
    print(_divider("═"))


def _step_banner(step: dict) -> None:
    print()
    print(_divider())
    print(f"  Step {step['number']}/{len(STEPS)}  ·  {step['name']}")
    print(f"  {step['description']}")
    print(_divider())


def _check_scripts_exist(steps: list) -> None:
    """Abort early if any script file is missing."""
    missing = [
        s["script"] for s in steps
        if not (BASE_DIR / s["script"]).exists()
    ]
    if missing:
        for m in missing:
            print(f"  ✗  Script not found: {BASE_DIR / m}")
        logger.error("Missing scripts: %s", missing)
        sys.exit(1)


def _run_step(step: dict, dry_run: bool = False) -> float:
    """
    Execute one pipeline step as a subprocess.

    Args:
        step:    Step dict from STEPS.
        dry_run: If True, print the command but do not execute it.

    Returns:
        Elapsed wall-clock seconds (0.0 for dry runs).

    Raises:
        SystemExit: If the subprocess exits with a non-zero return code.
    """
    script_path = BASE_DIR / step["script"]
    cmd = [sys.executable, str(script_path)]

    if dry_run:
        print(f"  [dry-run] Would run: {' '.join(cmd)}")
        return 0.0

    logger.info("Starting step %d: %s", step["number"], step["name"])
    start = time.perf_counter()

    result = subprocess.run(
        cmd,
        cwd=str(BASE_DIR),      # each script resolves paths relative to BASE_DIR
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,   # merge stderr into stdout for a single stream
    )

    elapsed = time.perf_counter() - start

    # Stream captured output to the terminal and to the pipeline log
    if result.stdout:
        for line in result.stdout.rstrip().splitlines():
            print(f"    {line}")
            logger.info("[%s] %s", step["name"], line)

    if result.returncode != 0:
        print()
        print(f"  ✗  Step {step['number']} ({step['name']}) FAILED "
              f"(exit code {result.returncode})")
        logger.error(
            "Step %d (%s) failed with exit code %d",
            step["number"], step["name"], result.returncode,
        )
        sys.exit(result.returncode)

    logger.info(
        "Step %d (%s) completed in %.1fs", step["number"], step["name"], elapsed
    )
    return elapsed


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the movie data pipeline end-to-end.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join([
            "Examples:",
            "  python run_pipeline.py               # full pipeline",
            "  python run_pipeline.py --start 3     # resume from data_processor",
            "  python run_pipeline.py --only 4      # analyze_data only",
            "  python run_pipeline.py --dry-run     # preview without executing",
        ]),
    )
    parser.add_argument(
        "--start",
        type=int,
        metavar="N",
        help="Start from step N (1–4). Skips earlier steps.",
    )
    parser.add_argument(
        "--only",
        type=int,
        metavar="N",
        help="Run only step N (1–4). Overrides --start.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be executed without running anything.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args = parse_args()

    # Resolve which steps to run
    if args.only is not None:
        steps_to_run = [s for s in STEPS if s["number"] == args.only]
        if not steps_to_run:
            print(f"  ✗  --only {args.only} is not a valid step (choose 1–{len(STEPS)}).")
            sys.exit(1)
    elif args.start is not None:
        steps_to_run = [s for s in STEPS if s["number"] >= args.start]
        if not steps_to_run:
            print(f"  ✗  --start {args.start} is not a valid step (choose 1–{len(STEPS)}).")
            sys.exit(1)
    else:
        steps_to_run = list(STEPS)

    started_at = datetime.now(timezone.utc)
    _header(f"Movie Data Pipeline  ·  {started_at.strftime('%Y-%m-%d %H:%M UTC')}")

    if args.dry_run:
        print("  [dry-run mode — no scripts will be executed]")

    print()
    print("  Steps queued:")
    for s in steps_to_run:
        marker = "  " if not args.dry_run else "  "
        print(f"    {s['number']}. {s['name']:20s} — {s['description']}")

    if not args.dry_run:
        _check_scripts_exist(steps_to_run)

    # ── Run each step ──────────────────────────────────────────────────── #
    timings: list = []
    for step in steps_to_run:
        _step_banner(step)
        elapsed = _run_step(step, dry_run=args.dry_run)
        timings.append((step["name"], elapsed))
        if not args.dry_run:
            print(f"\n  ✓  {step['name']} completed in {elapsed:.1f}s")

    # ── Summary ───────────────────────────────────────────────────────── #
    print()
    _header("Pipeline complete")
    print()

    if not args.dry_run:
        total = sum(t for _, t in timings)
        for name, t in timings:
            print(f"    {name:25s} {t:6.1f}s")
        print(_divider("─", 40))
        print(f"    {'Total':25s} {total:6.1f}s")
        print()
        print(f"  Outputs:")
        print(f"    data/raw/tmdb/        — TMDB JSON files")
        print(f"    data/raw/letterboxd/  — Letterboxd JSON files")
        print(f"    data/processed/       — movies.csv + movies.json")
        print(f"    data/analysis/plots/  — PNG visualizations")
        print(f"    REPORT.md")
        print(f"    logs/                 — per-script + pipeline logs")
        print()
        logger.info(
            "Pipeline finished in %.1fs  (steps: %s)",
            total, [s["name"] for s in steps_to_run],
        )


if __name__ == "__main__":
    main()