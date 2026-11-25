import os
import sys
import argparse
from scraper import scrape_books
from cleaner import deduplicate_records
from storage import save_to_csv, save_to_json, validate_dataset

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DEFAULT_CSV_PATH = os.path.join(DATA_DIR, "books_scraped.csv")
DEFAULT_JSON_PATH = os.path.join(DATA_DIR, "books_scraped.json")


def run_pipeline(max_pages: int = 3, csv_path: str = DEFAULT_CSV_PATH, json_path: str = DEFAULT_JSON_PATH):
    print("=" * 65)
    print("🚀 STARTING BOOKS.TOSCRAPE.COM EXTRACTION PIPELINE")
    print(f"Target Pages: {max_pages} (Minimum requirement: 2 pages / 20 products)")
    print("=" * 65)

    # 1. Scrape raw records
    raw_records = scrape_books(max_pages=max_pages)
    if not raw_records:
        print("[Fatal Error] Extraction returned 0 records. Check internet connection or site status.")
        sys.exit(1)

    # 2. Clean & Deduplicate
    clean_records, duplicates_dropped = deduplicate_records(raw_records, key="product_name")
    print(f"Deduplication complete: {len(clean_records)} unique records retained ({duplicates_dropped} duplicate(s) dropped).")

    # 3. Store datasets
    save_to_csv(clean_records, csv_path)
    save_to_json(clean_records, json_path)

    # 4. Validate output
    validation = validate_dataset(csv_path)

    print("\n" + "=" * 65)
    print("📊 DATASET EXTRACTION SUMMARY & QUALITY AUDIT")
    print("=" * 65)
    print(f"Total Products Scraped: {validation.get('total_records', 0)}")
    print(f"Duplicates Detected:    {validation.get('duplicate_titles', 0)}")
    print(f"Invalid / Null Prices:  {validation.get('invalid_prices', 0)}")
    print(f"Target Requirement Met: {'✓ PASS (>= 20 items)' if validation.get('is_valid') else '✗ FAIL'}")
    print(f"CSV Output:             {csv_path}")
    print(f"JSON Output:            {json_path}")
    print("=" * 65)

    if not validation.get("is_valid"):
        print("[Warning] Dataset failed one or more quality audits.")
        sys.exit(1)

    print("✓ Pipeline successfully executed end-to-end!")
    return clean_records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Books to Scrape catalogue dataset.")
    parser.add_argument("--pages", type=int, default=3, help="Number of pages to scrape (default: 3)")
    args = parser.parse_args()

    run_pipeline(max_pages=args.pages)
