import pytest
import sys
import os

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cleaner import (
    clean_price,
    clean_availability,
    clean_text,
    clean_rating,
    deduplicate_records,
)


def test_clean_price_standard_and_symbols():
    # Standard GBP currency format
    assert clean_price("£51.77") == 51.77
    # Trailing/leading whitespace
    assert clean_price("   £12.45   ") == 12.45
    # UTF-8 Mojibake prefix frequently found on Windows
    assert clean_price("Â£34.90") == 34.90
    # Other currency symbols
    assert clean_price("$99.95") == 99.95
    assert clean_price("€24.00") == 24.00


def test_clean_price_edge_cases():
    # None or non-numeric strings
    assert clean_price(None) is None
    assert clean_price("") is None
    assert clean_price("Price on request") is None
    assert clean_price("N/A") is None


def test_clean_availability_normalization():
    # Standard variants from books.toscrape.com
    assert clean_availability("In stock") == "In Stock"
    assert clean_availability("In stock (22 available)") == "In Stock"
    assert clean_availability("  in stock (1 available)  ") == "In Stock"

    # Out of stock or missing variants
    assert clean_availability("Out of stock") == "Out of Stock"
    assert clean_availability("") == "Out of Stock"
    assert clean_availability(None) == "Out of Stock"


def test_clean_text_unescaping_and_trimming():
    # HTML entity unescaping
    assert clean_text("A Light in the &amp; Attic") == "A Light in the & Attic"
    assert clean_text("Pride &amp; Prejudice") == "Pride & Prejudice"
    # Normalizing multiple consecutive spaces and newlines
    assert clean_text("  Sapiens:\n A Brief   History  ") == "Sapiens: A Brief History"


def test_clean_rating_class_extraction():
    assert clean_rating(["star-rating", "Three"]) == "Three"
    assert clean_rating(["star-rating", "One"]) == "One"
    assert clean_rating(["star-rating", "Five"]) == "Five"
    assert clean_rating([]) == "Not Rated"
    assert clean_rating(None) == "Not Rated"


def test_deduplicate_records_removes_exact_and_case_variants():
    sample_records = [
        {"product_name": "A Light in the Attic", "price": 51.77},
        {"product_name": "Tipping the Velvet", "price": 53.74},
        {"product_name": "a light in the attic", "price": 51.77},  # duplicate lowercase
        {"product_name": "Soumission", "price": 50.10},
        {"product_name": "Tipping the Velvet", "price": 53.74},  # duplicate exact
    ]

    unique, dropped = deduplicate_records(sample_records, key="product_name")

    assert len(unique) == 3
    assert dropped == 2
    titles = [item["product_name"].lower() for item in unique]
    assert titles == ["a light in the attic", "tipping the velvet", "soumission"]
