import subprocess

scripts = [
    "api_collector.py",
    "web_scraper.py",
    "data_processor.py",
    "analyze_data.py"
]

for script in scripts:
    print("running", script)
    subprocess.run(["python3", script])
