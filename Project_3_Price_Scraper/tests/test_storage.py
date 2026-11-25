import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage import save_to_csv, save_to_json, load_from_csv, load_from_json, validate_dataset


def test_storage_roundtrip_csv_and_json():
    sample_data = [
        {
            "product_name": "Test Book 1",
            "price": 19.99,
            "currency": "GBP",
            "url": "https://books.toscrape.com/test1",
            "availability": "In Stock",
            "timestamp": "2026-11-23T01:00:00Z",
            "rating": "Four",
        },
        {
            "product_name": "Test Book 2",
            "price": 29.50,
            "currency": "GBP",
            "url": "https://books.toscrape.com/test2",
            "availability": "In Stock",
            "timestamp": "2026-11-23T01:05:00Z",
            "rating": "Five",
        },
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "test.csv")
        json_path = os.path.join(tmpdir, "test.json")

        # 1. Test CSV
        assert save_to_csv(sample_data, csv_path) is True
        loaded_csv = load_from_csv(csv_path)
        assert len(loaded_csv) == 2
        assert loaded_csv[0]["product_name"] == "Test Book 1"
        assert float(loaded_csv[0]["price"]) == 19.99

        # 2. Test JSON
        assert save_to_json(sample_data, json_path) is True
        loaded_json = load_from_json(json_path)
        assert len(loaded_json) == 2
        assert loaded_json[1]["product_name"] == "Test Book 2"
        assert float(loaded_json[1]["price"]) == 29.50
