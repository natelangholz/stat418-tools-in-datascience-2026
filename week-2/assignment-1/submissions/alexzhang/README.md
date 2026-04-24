# NASA Web Log Analysis Pipeline - STAT 418

This project analyzes NASA web server logs from July and August 1995 using Bash scripting and Unix tools. It includes data acquisition, validation, analysis, and automated report generation.

---

## 📁 Project Structure

```
.
├── download_data.sh       # Downloads and validates log files
├── analyze_logs.sh        # Performs data analysis
├── generate_report.sh     # Generates markdown report
├── run_pipeline.sh        # Master script to run entire pipeline
├── NASA_Jul95.log         # July dataset (from running download_data.sh)
├── NASA_Aug95.log         # August dataset (from running download_data.sh)
└── report.md              # Final generated report
```

---

## ⚙️ Requirements

* Unix/Linux environment (or WSL on Windows)
* Bash shell
* Standard Unix tools:

  * `awk`
  * `sed`
  * `sort`
  * `uniq`
  * `curl` or `wget`

---

## 🚀 How to Run

### 1. Run the full pipeline

```bash
bash ./run_pipeline.sh
```

---

## 🔄 What the Pipeline Does

### Step 1: Data Acquisition

* Downloads July and August 1995 NASA logs
* Validates file existence and size
* Creates backup copies
* Handles download failures

---

### Step 2: Data Validation

* Ensures files are not empty
* Confirms expected log format

---

### Step 3: Data Analysis

The script computes:

#### Basic Analysis

* Top 10 hosts (excluding 404 errors)
* IP vs hostname percentage
* Top 10 requested URLs
* HTTP method distribution
* 404 error counts
* Most frequent response codes

#### Time-Based Analysis

* Peak activity hours
* Quiet hours
* Busiest and quietest days

#### Advanced Analysis

* Hurricane outage detection (August)
* Response size statistics (max and average)
* Error pattern analysis (time and host)

---

### Step 4: Report Generation

* Creates a comprehensive `report.md`
* Includes:

  * Summary statistics
  * July vs August comparison
  * Key findings and insights
  * ASCII visualizations
  * Full analysis output

---

### Step 5: Cleanup

* Removes temporary files

---

## 📊 Output

After running the pipeline, the main output is:

```
report.md
```

This file contains:

* Executive summary
* Key findings
* Detailed comparisons
* Visualizations
* Full analysis results

---

## ⚠️ Error Handling

The pipeline includes checks for:

* Missing or empty data files
* Script execution failures
* Report generation issues

If an error occurs, the pipeline stops and prints a descriptive message.

---

## 💡 Notes

* The pipeline is designed to be modular — each script can be run independently.
* Intermediate processing is done using streaming (no heavy temporary files).
* Designed for clarity, reproducibility, and efficiency.

---

## 📌 Example Usage

```bash
bash ./run_pipeline.sh
```

Output:

```
=== Starting NASA Log Analysis Pipeline ===
[1/4] Downloading data...
[2/4] Validating data...
[3/4] Running analysis...
[4/4] Generating report...
=== Pipeline completed successfully ===
```

---

## 👤 Author

Alex Zhang

---
