import time
import logging
from pathlib import Path
import sys
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format = "%(asctime)s | %(levelname)s | %(message)s",
    handlers = [
        logging.FileHandler("pipeline.log"),
        logging.StreamHandler()
    ]
)

def run_step(name, command):
    logging.info(f"Starting {name}")
    start = time.time()

    try:
        subprocess.run(command, check = True)
        elapsed = time.time() - start
        logging.info(f"Finished {name} in {elapsed:.4f}s.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed {name}.")
        logging.error(str(e))
        sys.exit(1)

def main():
    logging.info("Start Pipeline")
    logging.info("Starting requirements.")
    run_step("Install requirements", [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    logging.info("Finished requirements, starting api collector.")
    run_step("API Collector", [sys.executable, "api_collector.py"])
    logging.info("Finished api collector, starting web scaper.")
    run_step("Web Scraper", [sys.executable, "web_scraper.py"])
    logging.info("Finished web scraper, starting data processor.")
    run_step("Data Processor", [sys.executable, "data_processor.py"])
    logging.info("Finished data processor, starting analyze data.")
    run_step("Analyze Data", [sys.executable, "analyze_data.py"])
    logging.info("Pipeline complete")

if __name__ == "__main__":
    main()






