# 🚀 Insight Forge Internship Program — Master Portfolio

[![Insight Forge](https://img.shields.io/badge/Insight%20Forge-Internship%20Portfolio-blue.svg)](https://insightforge-pk.netlify.app)
[![Developer](https://img.shields.io/badge/Developer-Ahmed%20Naeem-orange.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production%20Ready-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/GitHub%20Actions-24%2F7%20Cloud%20Automation-2088FF.svg?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Test Suite](https://img.shields.io/badge/Tests-43%2F43%20Passing%20(100%25)-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)

> **Comprehensive GitHub Portfolio Repository** containing all 4 completed internship projects for the **Insight Forge Python Development & Backend Engineering Track**, engineered and submitted by **Ahmed Naeem**.

---

## 📌 Internship Progress Overview

| Module | Project Name | Directory | Tech Stack | Status | Documentation |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **Module 1** | **Project 1: Setup, Database & Auth** | [`Project_1_Wallet_API_Auth`](Project_1_Wallet_API_Auth/) | FastAPI, SQLAlchemy, SQLite/Postgres, Bcrypt, JWT | ✅ Completed | [README](Project_1_Wallet_API_Auth/README.md) • [Report](Project_1_Wallet_API_Auth/TASK_1_REPORT.md) |
| **Module 1** | **Project 2: Transactions & Deployment** | [`Project_2_Wallet_API_Transactions`](Project_2_Wallet_API_Transactions/) | FastAPI, Row Locking, Idempotency, SlowAPI, Docker | ✅ Completed | [README](Project_2_Wallet_API_Transactions/README.md) • [Report](Project_2_Wallet_API_Transactions/FINAL_PROJECT_REPORT.md) |
| **Module 2** | **Project 3: E-Commerce Price Scraper** | [`Project_3_Price_Scraper`](Project_3_Price_Scraper/) | Requests, BeautifulSoup4, Pandas, Regex | ✅ Completed | [README](Project_3_Price_Scraper/README.md) • [Report](Project_3_Price_Scraper/TASK_1_REPORT.md) |
| **Module 2** | **Project 4: Price Alert Automation Engine** | [`Project_4_Price_Tracker_Automation`](Project_4_Price_Tracker_Automation/) | Python Schedule, GitHub Actions Cron, Telegram/Email | ✅ Completed | [README](Project_4_Price_Tracker_Automation/README.md) • [Report](Project_4_Price_Tracker_Automation/FINAL_PROJECT_REPORT.md) |

---

## 📂 Repository Architecture

Each project is completely self-contained with its own source code, pinned dependencies (`requirements.txt`), automated test suites (`tests/`), technical submission reports, and detailed individual `README.md`:

```text
Insight_Forge_Internship/
│
├── 📁 Project_1_Wallet_API_Auth/              # Module 1 (Task 1): Foundation
│   ├── app/                                   # FastAPI Core, Models & Auth Routers
│   ├── scripts/seed_db.py                     # High-Performance Seed Ingestion (60,773 rows)
│   ├── seed_data/                             # Relational Schema & Raw CSVs
│   ├── tests/                                 # 9 Automated Unit & Auth Tests
│   ├── TASK_1_REPORT.md                       # Formal Task 1 Technical Report
│   ├── requirements.txt                       # Pinned Dependencies
│   └── README.md                              # Dedicated Project 1 Portfolio Documentation
│
├── 📁 Project_2_Wallet_API_Transactions/      # Module 1 (Task 2): Core Money Movements
│   ├── app/                                   # Atomic Transfers, Row Locking, Idempotency
│   ├── scripts/live_demo.py                   # Real-Time End-to-End Live Demonstration Script
│   ├── tests/                                 # 16 Automated Integration & Concurrency Tests
│   ├── Dockerfile & docker-compose.yml        # Multi-Container Setup (FastAPI + PostgreSQL 16)
│   ├── GlobalPay_Wallet_API.postman_col...    # Exported Postman Collection with Auth scripts
│   ├── render.yaml & Procfile                 # Cloud PaaS Deployment Manifests
│   ├── FINAL_PROJECT_REPORT.md                # 3-4 Page Comprehensive Module 1 Final Report
│   └── README.md                              # Dedicated Project 2 Portfolio Documentation
│
├── 📁 Project_3_Price_Scraper/                # Module 2 (Task 1): Extraction Engine
│   ├── scraper.py                             # Multi-Page BeautifulSoup Web Scraper
│   ├── cleaner.py                             # Regex Currency Parsing, Stock Normalization
│   ├── storage.py                             # CSV & JSON Exporter with Dataset Quality Audits
│   ├── main.py                                # CLI Pipeline Runner
│   ├── data/                                  # Extracted Datasets (60 books across 3 pages)
│   ├── tests/                                 # 7 Cleaning & Serialization Sanity Tests
│   ├── TASK_1_REPORT.md                       # Formal Task 1 Scraper Technical Report
│   └── README.md                              # Dedicated Project 3 Portfolio Documentation
│
└── 📁 Project_4_Price_Tracker_Automation/     # Module 2 (Task 2): Cloud Automation Engine
    ├── .github/workflows/price_check.yml      # 24/7 Unattended Cloud Cron Workflow
    ├── tracker.py                             # Stateful Price Comparison & Drop Alert Logic
    ├── main.py                                # Execution Runner (--once, --demo-alert, --interval)
    ├── data/price_history.csv                 # Append-Only Chronological Price History Log
    ├── logs/price_tracker.log                 # Timestamped Execution Audit Logs
    ├── tests/                                 # 11 Price Drop & State Persistence Tests
    ├── FINAL_PROJECT_REPORT.md                # Comprehensive Module 2 Final Automation Report
    └── README.md                              # Dedicated Project 4 Portfolio Documentation
```

---

## 🌟 Executive Project Summaries

### 💳 1. GlobalPay Digital Wallet Backend API (Projects 1 & 2)
A production-grade, secure digital wallet ledger designed to power consumer web and mobile fintech applications.
- **Identity & Access**: Bcrypt password hashing (cost 12), expiring HS256 JWT access tokens, and Pydantic response sanitization (zero password hash leakage).
- **Relational Data Scale**: Ingested and verified **5,000 Users**, **5,773 Wallets**, and **50,000 Transactions** from raw CSV files with zero integrity failures.
- **Atomic Money Movements**: Deposits, withdrawals, and peer-to-peer transfers execute in a single database transaction (`BEGIN ... COMMIT`) with automatic `ROLLBACK` on error.
- **Deadlock-Free Row-Level Locking**: Sorts wallet IDs in ascending order (`sorted([sender_id, receiver_id])`) and applies row locks (`with_for_update()`) to eliminate race conditions.
- **Stripe-Style Idempotency**: Client-supplied UUID `idempotency_key` ensures network retries never double-charge customers (`is_cached: true`).
- **Security & Infrastructure**: SlowAPI rate limiting (10 logins/min, 20 transfers/min), multi-container Docker Compose (FastAPI + PostgreSQL 16), and Postman collection.
- 👉 **Explore Project 1**: [`Project_1_Wallet_API_Auth/`](Project_1_Wallet_API_Auth/)
- 👉 **Explore Project 2**: [`Project_2_Wallet_API_Transactions/`](Project_2_Wallet_API_Transactions/)

---

### 📊 2. E-Commerce Price Tracker & Cloud Automation (Projects 3 & 4)
An unattended, 24/7 cloud automation pipeline that continuously monitors product pricing, maintains chronological price logs, and dispatches real-time alerts upon price drops.
- **Multi-Page Web Scraping**: Extracts product titles, pure numeric prices, currency, stock status, ratings, and URLs from [books.toscrape.com](https://books.toscrape.com) across paginated catalogues.
- **Data Hygiene**: Strips currency mojibake (`Â£` / `£`), unescapes HTML entities, normalizes stock status (`"In Stock"`), and deduplicates records.
- **Stateful History Tracking**: Appends historical checks to `price_history.csv` without overwriting prior records.
- **Intelligent Price Drop Detection**: Compares `current_price` vs `previous_price` and evaluates custom `target_price` thresholds with false-positive filtering.
- **Unattended Cloud Scheduling**: Configured via GitHub Actions (`.github/workflows/price_check.yml`) running on a 30-minute cron schedule, pulling repository secrets, and auto-committing updated history files back to GitHub.
- 👉 **Explore Project 3**: [`Project_3_Price_Scraper/`](Project_3_Price_Scraper/)
- 👉 **Explore Project 4**: [`Project_4_Price_Tracker_Automation/`](Project_4_Price_Tracker_Automation/)

---

## 🛠️ Unified Technology Stack

| Category | Technologies |
| :--- | :--- |
| **Backend Frameworks** | FastAPI, Uvicorn, Pydantic v2, Starlette |
| **ORM & Databases** | SQLAlchemy 2.0, PostgreSQL 16, SQLite |
| **Security & Auth** | Bcrypt (Passlib), PyJWT (HS256), SlowAPI (Rate Limiting), Dotenv |
| **Web Scraping & Data** | Requests, BeautifulSoup4, Pandas, Regex |
| **Automation & Cloud** | GitHub Actions (Cron CI/CD), Python Schedule, Telegram Bot API |
| **DevOps & Containers** | Docker, Docker Compose, Render/Railway manifests (`render.yaml`, `Procfile`) |
| **Testing & Quality** | Pytest, TestClient, In-Memory Fixtures, Automated Verifications |

---

## 🧪 Comprehensive Automated Test Results

All 4 projects feature dedicated automated test suites with **100% test pass rate**:

```text
======================================================================
  AUTOMATED TEST SUITE EXECUTION SUMMARY
======================================================================
✓ Project 1 (Auth & Wallet Foundation):        9 /  9 PASSED (100%)
✓ Project 2 (Transactions, Locks & Idempotency): 16 / 16 PASSED (100%)
✓ Project 3 (Scraper Engine & Data Cleaner):     7 /  7 PASSED (100%)
✓ Project 4 (Price Tracker & Alert Automation): 11 / 11 PASSED (100%)
----------------------------------------------------------------------
TOTAL TESTS VERIFIED ACROSS ALL PROJECTS:      43 / 43 PASSED (100%)
======================================================================
```

---

## 🚀 How to Run the Projects Locally

Clone this repository and enter any project directory to run it independently:

### Running Project 1 or Project 2 (FastAPI Wallet API)
```bash
cd Project_2_Wallet_API_Transactions

# 1. Setup virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux / macOS

# 2. Install dependencies & seed database
pip install -r requirements.txt
python scripts/seed_db.py

# 3. Start API server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Open interactive documentation at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)*

### Running Project 3 (Price Scraper)
```bash
cd Project_3_Price_Scraper
pip install -r requirements.txt
python main.py --pages 3
```

### Running Project 4 (Automated Price Tracker)
```bash
cd Project_4_Price_Tracker_Automation
pip install -r requirements.txt

# Run demo with simulated 15% price drop alert:
python main.py --demo-alert

# Run continuous 15-minute background monitoring:
python main.py --interval 15
```

---

## 👨‍💻 Author & Intern Information

- **Intern Name**: **Ahmed Naeem**
- **Organization**: **Insight Forge**
- **Track**: Python Development & Backend Engineering Track
- **Submission Date**: November 2026
- **Portfolio Status**: 4 of 4 Projects Completed (100% Submission Ready)
