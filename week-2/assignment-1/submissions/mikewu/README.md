# How to Run

From the repo root:

```bash
cd week-2/assignment-1/submissions/mikewu
chmod +x download_data.sh analyze_logs.sh generate_report.sh run_pipeline.sh
./run_pipeline.sh
```

Run scripts one-by-one if needed:

```bash
./download_data.sh ./data
./analyze_logs.sh ./data/NASA_Jul95.log ./data/NASA_Aug95.log
./generate_report.sh
```

Output report:

- `REPORT.md`
