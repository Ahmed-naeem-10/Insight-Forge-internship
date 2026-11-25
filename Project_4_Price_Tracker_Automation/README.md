# 🚨 Price Alert Automation Engine (Project 4 — Task 2)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![GitHub Actions](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20Cron-2088FF.svg?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Pandas](https://img.shields.io/badge/Data-Pandas-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Schedule](https://img.shields.io/badge/Scheduler-Python%20Schedule-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-11%2F11%20Passing-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Status](https://img.shields.io/badge/Status-Project%204%20Complete-success.svg)]()

> Official submission for **Module 2: Project 4 (Price Alert Automation Engine: Scheduled Monitoring, Alerts & Cloud Deployment)** of the Insight Forge Python Development Internship.

---

## 📌 1. Project Overview & Description

A price tracker that requires someone to babysit their laptop is not real automation. Real automation pipelines operate unattended in the cloud for months, tracking market changes, preserving price history, and alerting users the moment a price drops without false positives or credential leaks.

Building upon the Project 3 scraper, **Project 4** transforms data extraction into an end-to-end cloud monitoring product:
- **Stateful Price Comparison**: Automatically matches incoming scrape records against historical prices stored in `price_history.csv` to calculate `price_change` and `price_drop_pct`.
- **Intelligent Price Drop Detection**: Triggers alerts when prices drop below previous records or fall beneath product `target_price` thresholds.
- **Anti-Spam & False Positive Filters**: Suppresses duplicate alerts for products that remain at a low price, while discarding corrupt £0.00 scrape errors.
- **Multi-Channel Alert Dispatch**: Formatted console notifications, file logs, and optional real-time **Telegram Bot API** and **Email** dispatch.
- **Unattended Cloud Scheduling (GitHub Actions)**: Automated `.github/workflows/price_check.yml` workflow executing on a 30-minute cron schedule, pulling secrets securely, and auto-committing updated history files back to the repository.

---

## 📸 2. Project Visual Showcase & Terminal Execution

### Live Price Drop Detection Showcase (`python main.py --demo-alert`)
```text
=================================================================
🧪 RUNNING DEMONSTRATION CYCLE (SIMULATING 15% PRICE DROP)
=================================================================
[INFO] --- Starting Scheduled Price Tracker Cycle ---
Crawling complete: 40 records gathered across 2 page(s).
[INFO] Appended 40 records to history file: data/price_history.csv
[INFO] Cycle finished. Tracked: 40 | Alerts Fired: 0

[INFO] --- Starting Scheduled Price Tracker Cycle ---
Crawling complete: 40 records gathered across 2 page(s).
[INFO] ============================================================
[INFO] 🚨 PRICE DROP ALERT: 1 PRODUCT(S) DROPPED IN PRICE!
[INFO] ============================================================
[WARNING] 🔔 [ALERT] 'A Light in the Attic' dropped to £44.00 (Previous: £51.77 | Change: £-7.77 / -15.01%)
[INFO] Appended 40 records to history file: data/price_history.csv
[INFO] Cycle finished. Tracked: 40 | Alerts Fired: 1
```

---

## 🛠️ 3. Tools & Technologies Used

| Category | Technology | Usage in Project 4 |
| :--- | :--- | :--- |
| **Language** | **Python 3.10+** | Core automation logic and data comparison. |
| **Local Scheduling** | **`schedule`** | Python scheduling library for continuous local interval runs. |
| **Cloud Scheduling** | **GitHub Actions** | Unattended cloud cron workflow (`*/30 * * * *`) with Git auto-commit. |
| **Data History** | **`pandas`** | Multi-run tabular history appending and price diff calculation. |
| **Notifications** | **Telegram Bot / smtplib** | Multi-channel alert dispatching to mobile and email. |
| **Secrets Protection** | **`python-dotenv`** | Secure local `.env` and GitHub Repository Secrets management. |
| **Testing** | **`pytest`** | Automated testing for comparison logic and history persistence. |

---

## 📁 4. Project Architecture & File Organization

```text
project_4/
├── .github/
│   └── workflows/
│       └── price_check.yml  # Cloud cron automation workflow (GitHub Actions)
├── scraper.py               # Extraction engine (requests + BeautifulSoup)
├── cleaner.py               # Data cleaning and normalization routines
├── storage.py               # Dataset persistence handlers
├── tracker.py               # Stateful comparison, alert triggers, history appending
├── main.py                  # CLI runner (--once, --demo-alert, --interval)
├── tests/                   # Automated unit test suite
│   ├── test_tracker.py      # Tests for price drop detection & history logic
│   └── test_cleaner.py      # Tests for currency parsing and normalization
├── data/
│   └── price_history.csv    # Append-only chronological price history log
├── logs/
│   └── price_tracker.log    # Structured runtime execution log
├── requirements.txt         # Pinned dependency manifest
├── pytest.ini               # Pytest configuration
├── .env.example             # Secrets template (Telegram & Email placeholders)
├── FINAL_PROJECT_REPORT.md  # Comprehensive Final Project Report (Projects 3 & 4)
└── README.md                # Project 4 documentation
```

---

## ⚡ 5. Key Features & Quality Benchmarks

1. **Continuous 24/7 Monitoring**: Runs in the cloud via GitHub Actions cron without requiring your laptop to remain on.
2. **Append-Only History**: `price_history.csv` is never overwritten; each scheduled run appends historical pricing rows.
3. **Smart Alerting**: Only triggers when `price_change < 0` or price crosses below `target_price`, eliminating duplicate spam.
4. **Zero Secret Leaks**: All credentials are kept in `.env` (git-ignored) and referenced in the cloud as `${{ secrets.X }}`.
5. **False-Positive Immunity**: Discards £0.00 or corrupt scraping errors to avoid erroneous alert triggers.

---

## 🧪 6. Automated Testing Suite

Execute the automated test suite:
```bash
pytest -v
```

### Execution Results (11/11 Passing):
```text
tests/test_cleaner.py::test_clean_price_standard_and_symbols PASSED      [  9%]
tests/test_cleaner.py::test_clean_price_edge_cases PASSED                [ 18%]
tests/test_cleaner.py::test_clean_availability_normalization PASSED      [ 27%]
tests/test_cleaner.py::test_clean_text_unescaping_and_trimming PASSED    [ 36%]
tests/test_cleaner.py::test_clean_rating_class_extraction PASSED         [ 45%]
tests/test_cleaner.py::test_deduplicate_records_removes_exact_and_case_variants PASSED [ 54%]
tests/test_tracker.py::test_compare_prices_detects_real_price_drop PASSED [ 63%]
tests/test_tracker.py::test_compare_prices_no_drop_when_price_increases_or_steady PASSED [ 72%]
tests/test_tracker.py::test_target_price_threshold_triggers_alert PASSED [ 81%]
tests/test_tracker.py::test_false_positive_filtering_zero_prices PASSED  [ 90%]
tests/test_tracker.py::test_history_appends_without_overwriting PASSED   [100%]

============================= 11 passed in 2.12s =============================
```

---

## 🚀 7. Quick Start & Execution

### Local Setup
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux / macOS

pip install -r requirements.txt
cp .env.example .env
```

### Run Commands:
```bash
# 1. Run a single tracking check immediately:
python main.py --once

# 2. Run with simulated price drop demo (triggers alert):
python main.py --demo-alert

# 3. Run continuous local scheduler (every 15 minutes):
python main.py --interval 15
```

---

## 📄 8. Submission Deliverables
- [FINAL_PROJECT_REPORT.md](FINAL_PROJECT_REPORT.md) — Comprehensive technical report covering Projects 3 & 4.
- [.github/workflows/price_check.yml](.github/workflows/price_check.yml) — GitHub Actions cloud workflow.
- [data/price_history.csv](data/price_history.csv) — Real historical price tracking dataset.
