# Final Project Report — Price Alert Automation Engine
**Python Development Internship | Automation Pipeline Track**  
**Comprehensive Deliverable: Module 2 (Projects 3 & 4: Steps 1–24)**  
**Author / Engineer**: Internship Candidate  
**Target Website**: `https://books.toscrape.com`  

---

## 1. Project Overview

The Price Alert Automation Engine is a production-grade, unattended cloud automation pipeline designed to monitor e-commerce product pricing, maintain historical price logs, and dispatch immediate notifications whenever a price drops or crosses beneath a defined threshold. Covering both the data extraction engine (Project 3) and the continuous scheduling and alert infrastructure (Project 4), the pipeline operates 24/7 in the cloud without requiring local machine runtime.

---

## 2. Architecture & Pipeline Approach

The architecture connects extraction, data cleaning, stateful price comparison, alert dispatch, and cloud persistence into a unified pipeline:

```text
[Cloud Cron Scheduler (GitHub Actions / schedule)]
                        │
                        ▼
           [Scraper Engine (scraper.py)]
         Extracts live HTML from target pages
                        │
                        ▼
           [Data Cleaner (cleaner.py)]
        Strips £/Â£, trims text, deduplicates
                        │
                        ▼
          [Price Tracker (tracker.py)]
      Loads previous run from price_history.csv
   Compares current_price vs previous_price
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
  [Price Dropped?]              [No Drop / Steady]
         │                             │
    YES: 🚨 Fire Alert                 │
 (Console, Logs, Telegram/Email)       │
         │                             │
         └──────────────┬──────────────┘
                        ▼
     [Append to data/price_history.csv]
                        │
                        ▼
 [Git Auto-Commit & Push (Persistent State)]
```

### Component Breakdown
1. **`scraper.py`**: Fetches HTML with user-agent headers and multi-page pagination traversal.
2. **`cleaner.py`**: Converts raw price strings to clean numeric floats and normalizes availability.
3. **`tracker.py`**: Loads previous pricing state, calculates `price_change` and `price_drop_pct`, evaluates alert conditions, and appends records.
4. **`main.py`**: CLI orchestrator providing `--once`, `--demo-alert`, and `--interval` continuous scheduling flags.
5. **`.github/workflows/price_check.yml`**: Cloud execution workflow running on a cron schedule (`*/30 * * * *`).

---

## 3. Security & Secrets Management

In adherence to industry security best practices:
- **No Hardcoded Credentials**: API tokens, chat IDs, and SMTP passwords are never hardcoded inline in Python source files.
- **Local Isolation**: Locally, secrets are stored in `.env` and loaded via `python-dotenv`. The `.env` file is permanently excluded from Git through `.gitignore`.
- **Cloud Secrets**: In GitHub Actions, credentials (`TELEGRAM_BOT_TOKEN`, `EMAIL_PASSWORD`) are injected securely at runtime via **GitHub Repository Secrets** (`${{ secrets.X }}`).
- **Template Sharing**: A clean `.env.example` file is committed to the repository with placeholder values to guide contributors.

---

## 4. Deployment (Cloud Unattended Scheduling)

The pipeline is containerized and scheduled via **GitHub Actions** (`.github/workflows/price_check.yml`):
- **Cron Trigger**: `cron: '*/30 * * * *'` (runs every 30 minutes).
- **Manual Dispatch**: `workflow_dispatch` enabled for on-demand execution via the GitHub dashboard.
- **Persistence Across Runs**: After each run, the workflow automatically stages `data/price_history.csv` and `logs/price_tracker.log`, commits the update using `github-actions[bot]`, and pushes the changes back to the repository.

---

## 5. Challenges & Technical Solutions

| Challenge | Problem | Engineering Solution |
| :--- | :--- | :--- |
| **1. Stateful Comparison Across Runs** | Script restarts wipe memory state; comparison requires previous run history. | Implemented `load_latest_prices_from_history()` reading `price_history.csv` to map `product_name -> latest_price` dynamically. |
| **2. Avoiding Duplicate Alerts** | A price staying low across multiple runs shouldn't trigger duplicate alerts every 15 minutes. | Alerts trigger only when `price_change < 0` (a fresh drop occurred during the current cycle) or when crossing below `target_price`. |
| **3. False Positive Protection** | Network errors or missing tags could yield £0.00, falsely simulating a 100% price drop. | Filtered out zero and non-numeric prices before comparison (`if curr_price <= 0: continue`). |
| **4. Cloud State Loss** | GitHub Actions runners are ephemeral; uncommitted changes are discarded when the job ends. | Added a post-run step in the workflow to commit and push updated history files back to GitHub. |

---

## 6. Results & Demonstration Evidence

### Live Simulated Alert Output (`python main.py --demo-alert`)
```text
2026-11-23 01:53:54 [INFO] --- Starting Scheduled Price Tracker Cycle ---
Crawling complete: 40 records gathered across 2 page(s).
2026-11-23 01:53:56 [INFO] Appended 40 records to history file: data/price_history.csv
2026-11-23 01:53:56 [INFO] Cycle finished. Tracked: 40 | Alerts Fired: 0

2026-11-23 01:53:56 [INFO] --- Starting Scheduled Price Tracker Cycle ---
Crawling complete: 40 records gathered across 2 page(s).
2026-11-23 01:53:58 [INFO] ============================================================
2026-11-23 01:53:58 [INFO] 🚨 PRICE DROP ALERT: 1 PRODUCT(S) DROPPED IN PRICE!
2026-11-23 01:53:58 [INFO] ============================================================
2026-11-23 01:53:58 [WARNING] 🔔 [ALERT] 'A Light in the Attic' dropped to £44.00 (Previous: £51.77 | Change: £-7.77 / -15.01%)
2026-11-23 01:53:58 [INFO] Appended 40 records to history file: data/price_history.csv
2026-11-23 01:53:58 [INFO] Cycle finished. Tracked: 40 | Alerts Fired: 1
```

### Automated Unit Test Results (`pytest -v`)
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

## 7. Conclusion

The Price Alert Automation Engine meets 100% of the project specification:
- Real-time web scraping with multi-page pagination.
- Stateful price history logging that grows over time.
- Accurate detection of price drops and target threshold crossings with anti-spam suppression.
- Cloud scheduling via GitHub Actions ensuring unattended 24/7 reliability.
