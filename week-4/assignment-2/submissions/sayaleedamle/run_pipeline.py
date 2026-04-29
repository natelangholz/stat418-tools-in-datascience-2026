import subprocess
import sys
import os

BASE = 'stat418-tools-in-datascience-2026/week-4/assignment-2/submissions/sayaleedamle'

STEPS = [
    ('1. TMDB API Collection', 'api_collector.py'),
    ('2. Letterboxd Scraping',  'web_scrapper.py'),
    ('3. Data Processing',      'data_processor.py'),
    ('4. Analysis',             'analyze_data.py'),
]

def run(label: str, script: str):
    path = os.path.join(BASE, script)
    print(f'\n{"="*55}')
    print(f'  {label}')
    print(f'{"="*55}')
    result = subprocess.run([sys.executable, path])
    if result.returncode != 0:
        print(f'\n[FAILED] {script} exited with code {result.returncode}. Stopping.')
        sys.exit(result.returncode)
    print(f'[DONE] {script}')

if __name__ == '__main__':
    for label, script in STEPS:
        run(label, script)
    print('\nPipeline complete.')
