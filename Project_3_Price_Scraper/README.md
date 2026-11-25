# 📚 E-Commerce Price Tracker & Scraper Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![BeautifulSoup](https://img.shields.io/badge/Scraping-BeautifulSoup4-green.svg)](https://www.crummy.com/software/BeautifulSoup/)
[![Pandas](https://img.shields.io/badge/Data-Pandas-150458.svg?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Tests](https://img.shields.io/badge/Tests-Pytest%20100%25%20Passing-brightgreen.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

> A robust, fault-tolerant, and modular Python web scraping automation pipeline designed to extract, clean, validate, and persist live e-commerce catalog data from [Books to Scrape](https://books.toscrape.com) across multiple paginated pages.

---

## 📌 1. Project Overview & Description

Retail analytics companies and consumers require continuous market intelligence to track pricing fluctuations, detect promotional discounts, and monitor product stock availability.

This project delivers **Task 1 of the Insight Forge Automation Pipeline Track (Project 3)**:
- Engineered a modular data extraction pipeline that crawls multi-page catalogues without hitting rate limits or memory bottlenecks.
- Implemented automated text normalization, regex price extraction (stripping `£` / `Â£` mojibake), and HTML entity unescaping.
- Built automated deduplication logic to maintain 100% data uniqueness.
- Generated clean, structured datasets in both **CSV** and **JSON** formats, validated against data quality standards.

---

## 📸 2. Project Visual Showcase & Terminal Execution

```text
=================================================================
🚀 STARTING BOOKS.TOSCRAPE.COM EXTRACTION PIPELINE
Target Pages: 3 (Minimum requirement: 2 pages / 20 products)
=================================================================
[1/3] Fetching: https://books.toscrape.com/catalogue/page-1.html
[2/3] Fetching: https://books.toscrape.com/catalogue/page-2.html
[3/3] Fetching: https://books.toscrape.com/catalogue/page-3.html
Crawling complete: 60 records gathered across 3 page(s).
Deduplication complete: 60 unique records retained (0 duplicate(s) dropped).
✓ Saved 60 records to CSV: data/books_scraped.csv
✓ Saved 60 records to JSON: data/books_scraped.json

=================================================================
📊 DATASET EXTRACTION SUMMARY & QUALITY AUDIT
=================================================================
Total Products Scraped: 60
Duplicates Detected:    0
Invalid / Null Prices:  0
Target Requirement Met: ✓ PASS (>= 20 items)
CSV Output:             data/books_scraped.csv
JSON Output:            data/books_scraped.json
=================================================================
✓ Pipeline successfully executed end-to-end!
```

---

## 🛠️ 3. Tools & Technologies Used

| Category | Technology | Purpose in Project |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core language for modular pipeline implementation. |
| **HTTP Client** | `requests` | Network requests with headers, session reuse, and timeout handling. |
| **HTML Parser** | `BeautifulSoup4` | DOM traversal, CSS selector matching, and attribute extraction. |
| **Data Processing** | `pandas` | Tabular data manipulation, schema enforcement, and CSV/JSON export. |
| **Data Cleaning** | `re`, `html` | Regex-based price cleaning, mojibake resolution, HTML unescaping. |
| **Testing** | `pytest` | Unit testing for cleaning routines, deduplication, and file I/O. |
| **Config & Secrets** | `python-dotenv` | Environment variable isolation and local secret management. |

---

## 📁 4. Project Architecture & File Organization

The codebase adheres strictly to professional modular design principles, isolating data extraction from data cleaning and persistence:

```text
new_project/
├── scraper.py          # Core scraping logic & pagination crawler
├── cleaner.py          # Data normalization, regex price cleaning, deduplication
├── storage.py          # Multi-format persistence (CSV/JSON) & quality validation
├── main.py             # CLI pipeline orchestrator with parameter parsing
├── tests/              # Automated unit tests
│   ├── test_cleaner.py # Unit tests for cleaning and normalization
│   └── test_storage.py # Serialization roundtrip tests
├── data/               # Exported dataset artifacts
│   ├── books_scraped.csv
│   └── books_scraped.json
├── requirements.txt    # Pinned dependency manifest
├── pytest.ini          # Pytest test configuration
├── TASK_1_REPORT.md    # Formal Task 1 technical submission report
└── README.md           # Recruiter-facing portfolio documentation
```

---

## 📊 5. Data Dictionary (Extracted Schema)

Every record captured by the scraper conforms to the following strict data contract:

| Field Name | Data Type | Example | Description |
| :--- | :---: | :--- | :--- |
| `product_name` | `string` | `"A Light in the Attic"` | Unabbreviated book title extracted from `<h3><a title="...">`. |
| `price` | `float` | `51.77` | Pure numeric float without currency symbols (stripped `£`/`Â£`). |
| `currency` | `string` | `"GBP"` | ISO currency code (fixed to British Pounds). |
| `url` | `string` | `"https://books.toscrape.com/..."` | Absolute HTTP link to the product's detail page. |
| `availability` | `string` | `"In Stock"` | Normalized stock status (`"In Stock"` or `"Out of Stock"`). |
| `timestamp` | `string` | `"2026-11-23T01:25:00Z"` | ISO-8601 UTC timestamp of extraction. |
| `rating` *(Bonus)*| `string` | `"Three"` | Star rating extracted from CSS class names (`One` to `Five`). |

---

## ⚡ 6. Key Features & Quality Benchmarks

- **Zero Data Loss & Pagination**: Dynamically navigates `li.next` links to crawl all designated catalogue pages.
- **Mojibake & Encoding Safety**: Corrects Windows UTF-8/CP-1252 character mismatches (`Â£` -> `£` -> `float`).
- **Resilient Error Handling**: Wrapped in `requests.exceptions.RequestException` blocks with 15-second timeouts to eliminate hanging processes.
- **Data Integrity Assurance**:
  - **60 books scraped** (300% above the 20-product minimum).
  - **0 duplicate records** retained.
  - **100% valid numeric prices** with zero missing values.

---

## 🧪 7. Automated Testing & Verification

Run the automated test suite:
```bash
pytest -v
```

### Test Suite Execution Output:
```text
tests/test_cleaner.py::test_clean_price_standard_and_symbols PASSED      [ 14%]
tests/test_cleaner.py::test_clean_price_edge_cases PASSED                [ 28%]
tests/test_cleaner.py::test_clean_availability_normalization PASSED      [ 42%]
tests/test_cleaner.py::test_clean_text_unescaping_and_trimming PASSED    [ 57%]
tests/test_cleaner.py::test_clean_rating_class_extraction PASSED         [ 71%]
tests/test_cleaner.py::test_deduplicate_records_removes_exact_and_case_variants PASSED [ 85%]
tests/test_storage.py::test_storage_roundtrip_csv_and_json PASSED        [100%]

============================== 7 passed in 3.06s ==============================
```

---

## 🚀 8. Quick Start Guide

### Step 1: Clone Repository & Setup Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Linux / macOS
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run Extraction Pipeline
```bash
python main.py --pages 3
```

---

## 📄 9. Documentation Deliverables
- [TASK_1_REPORT.md](TASK_1_REPORT.md) — Comprehensive technical report covering objectives, schema design, challenges & solutions, and quality audits.
- [data/books_scraped.csv](data/books_scraped.csv) — 60-product scraped dataset in CSV format.
- [data/books_scraped.json](data/books_scraped.json) — 60-product scraped dataset in JSON format.
