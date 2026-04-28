import subprocess
import sys


def run_pipeline() -> None:
    scripts = [
        "api_collector.py",
        "web_scraper.py",
        "data_processor.py",
        "analyze_data.py",
    ]

    for script in scripts:
        print(f"Running {script}...")
        result = subprocess.run([sys.executable, script])
        if result.returncode != 0:
            print(f"{script} failed with exit code {result.returncode}; stopping pipeline.")
            sys.exit(result.returncode)

    print("Pipeline complete.")


if __name__ == "__main__":
    run_pipeline()
