# Project Task 1 Report — E-Commerce Price Scraper
**Python Development Internship | Automation Pipeline Track**  
**Project Task 1 of 2: Scraper Engine & Dataset Generation**  
**Target Website**: `https://books.toscrape.com`  
**Author / Engineer**: Internship Candidate  

---

## 1. Objective

The objective of Task 1 was to build a modular, fault-tolerant Python web scraper to collect live e-commerce product information from the practice online bookstore [books.toscrape.com](https://books.toscrape.com). The system traverses multi-page pagination, extracts core product attributes, cleans messy price and availability text, deduplicates records, and exports structured CSV and JSON datasets ready for automated tracking in Task 2.

---

## 2. Project Setup

The scraper follows a production-grade modular architecture separating extraction, cleaning, storage, and orchestration:

```text
new_project/
├── scraper.py          # Core scraping logic (requests + BeautifulSoup, pagination loop)
├── cleaner.py          # Data cleaning (stripping £, normalizing stock, unescaping HTML)
├── storage.py          # Persistence layer (CSV/JSON export via pandas, quality validation)
├── main.py             # CLI Entry point (orchestrates scraper -> cleaner -> storage)
├── tests/              # Unit & sanity tests (pytest)
│   ├── test_cleaner.py # Validates price extraction, text normalization, deduplication
│   └── test_storage.py # Validates CSV/JSON serialization and roundtrips
├── data/               # Output directory for exported datasets
│   ├── books_scraped.csv
│   └── books_scraped.json
├── requirements.txt    # Pinned dependencies (requests, beautifulsoup4, pandas, pytest)
├── pytest.ini          # Test runner configuration
└── .gitignore          # Excludes environments, caches, and secrets
```

### Installation & Execution
```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate      # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the complete pipeline
python main.py --pages 3

# 4. Run automated tests
pytest -v
```

---

## 3. Data Fields Collected

All 6 required fields plus bonus fields were extracted using semantic CSS selectors:

| Field | Target Tag / Attribute | Processing & Normalization |
| :--- | :--- | :--- |
| `product_name` | `article.product_pod h3 a[title]` | Extracted full title attribute; unescaped HTML entities (e.g. `&amp;` -> `&`) and trimmed whitespace. |
| `price` | `article.product_pod p.price_color` | Stripped `£` and `Â£` symbols; parsed via regex into a standard floating-point number (e.g. `51.77`). |
| `currency` | Constant literal (`GBP`) | Verified against site specifications; fixed to ISO `GBP`. |
| `url` | `article.product_pod h3 a[href]` | Converted relative URLs (`a-light.../index.html`) to full absolute URLs using `urllib.parse.urljoin`. |
| `availability` | `article.product_pod p.availability` | Normalized mixed text (e.g. `"In stock (22 available)"`) into binary `"In Stock"` or `"Out of Stock"`. |
| `timestamp` | System clock (UTC) | Generated at scrape time using `datetime.now(timezone.utc).isoformat()`. |
| `rating` *(Bonus)* | `article.product_pod p.star-rating` | Parsed second CSS class (`One`, `Two`, `Three`, `Four`, `Five`) into title-cased rating string. |

---

## 4. Challenges & Technical Fixes

| Scraping Challenge | Problem Encountered | Engineering Solution Implemented |
| :--- | :--- | :--- |
| **1. Multi-Page Pagination** | Products are split across 50 pages; a naive script stops at page 1. | Implemented dynamic pager detection in `scraper.py` searching for `li.next a[href]`, dynamically joining relative links with `urljoin`. |
| **2. Windows Encoding Mojibake** | Raw `response.text` produced `Â£51.77` due to Windows-1252 default decoding. | Explicitly enforced `response.encoding = 'utf-8'` on the HTTP response before parsing, followed by regex cleanup in `cleaner.clean_price()`. |
| **3. Inconsistent Stock Text** | Stock strings contain extra whitespace, newlines, and variable availability counts. | Developed `clean_availability()` in `cleaner.py` utilizing case-insensitive substring detection (`"in stock" in text`). |
| **4. Duplicate Records** | Re-crawling or overlapping category pages could save duplicate entries. | Implemented `deduplicate_records()` using an in-memory normalized title set, discarding redundant records and reporting dropped count. |
| **5. Truncated Titles** | Visible anchor text (`a.text`) truncates long titles with ellipses (`...`). | Extracted title from `a['title']` attribute instead of inner text, preserving full unabbreviated book titles. |
| **6. Network Timeouts** | Remote latency can hang requests indefinitely. | Implemented explicit `timeout=15` and wrapped HTTP calls in `requests.exceptions.RequestException` blocks. |

---

## 5. Run Summary & Quality Audit

The pipeline was executed across 3 catalogue pages. The output dataset was subjected to automated validation in `storage.validate_dataset()`:

- **Target Website**: `https://books.toscrape.com/catalogue/`
- **Pages Crawled**: **3 pages** (exceeds the 2-page minimum requirement)
- **Total Products Scraped**: **60 books** (exceeds the 20-product minimum requirement by 300%)
- **Duplicate Records**: **0** (all records verified unique)
- **Missing / Null Prices**: **0** (100% of records have valid numeric prices)
- **Export Formats**:
  - CSV: `new_project/data/books_scraped.csv`
  - JSON: `new_project/data/books_scraped.json`
- **Price Range**: Min = £10.00, Max = £59.99, Avg = £35.07

---

## 6. Confirmation Statement

I confirm that the Task 1 scraper engine and dataset satisfy every quality benchmark defined in Slide 8:
- [x] Zero duplicate product records.
- [x] Target page range crawled completely without skipping.
- [x] Every price is a clean numeric float with zero currency symbols.
- [x] Every required field (`product_name`, `price`, `currency`, `url`, `availability`, `timestamp`) is populated for all 60 records.
- [x] The script fails gracefully with robust exception handling.
- [x] All 7 automated unit tests in `tests/` pass with 100% success.
