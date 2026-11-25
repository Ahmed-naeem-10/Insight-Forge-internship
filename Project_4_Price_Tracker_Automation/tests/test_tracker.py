import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tracker import (
    compare_prices,
    append_to_history,
    load_latest_prices_from_history,
)


def test_compare_prices_detects_real_price_drop():
    scraped_records = [
        {"product_name": "A Light in the Attic", "price": 45.00, "currency": "GBP", "url": "https://..."},
        {"product_name": "Tipping the Velvet", "price": 53.74, "currency": "GBP", "url": "https://..."},
    ]
    previous_prices = {
        "A Light in the Attic": 51.77,  # Was £51.77, now £45.00 (Price dropped!)
        "Tipping the Velvet": 53.74,   # Same price
    }

    history, alerts = compare_prices(scraped_records, previous_prices)

    assert len(history) == 2
    assert len(alerts) == 1

    drop_item = alerts[0]
    assert drop_item["product_name"] == "A Light in the Attic"
    assert drop_item["alert_triggered"] is True
    assert drop_item["price_change"] == -6.77
    assert drop_item["price_drop_pct"] < 0


def test_compare_prices_no_drop_when_price_increases_or_steady():
    scraped_records = [
        {"product_name": "Soumission", "price": 55.00, "currency": "GBP"},
    ]
    previous_prices = {
        "Soumission": 50.10,  # Price increased from £50.10 to £55.00
    }

    history, alerts = compare_prices(scraped_records, previous_prices)

    assert len(history) == 1
    assert len(alerts) == 0
    assert history[0]["alert_triggered"] is False
    assert history[0]["price_change"] == 4.90


def test_target_price_threshold_triggers_alert():
    scraped_records = [
        {"product_name": "Sharp Objects", "price": 38.00, "currency": "GBP"},
    ]
    # Target price explicitly set at £40.00
    custom_targets = {"Sharp Objects": 40.00}
    previous_prices = {"Sharp Objects": 38.00}

    history, alerts = compare_prices(scraped_records, previous_prices, custom_targets=custom_targets)

    assert len(alerts) == 1
    assert alerts[0]["alert_triggered"] is True
    assert alerts[0]["current_price"] < alerts[0]["target_price"]


def test_false_positive_filtering_zero_prices():
    # If scraper returns £0.00 due to parsing failure, it must be discarded
    scraped_records = [
        {"product_name": "Corrupt Item", "price": 0.00, "currency": "GBP"},
        {"product_name": "Valid Item", "price": 25.00, "currency": "GBP"},
    ]
    history, alerts = compare_prices(scraped_records, {})
    assert len(history) == 1
    assert history[0]["product_name"] == "Valid Item"


def test_history_appends_without_overwriting():
    run_1 = [
        {"product_name": "Book A", "current_price": 50.0, "previous_price": 50.0, "price_change": 0.0, "run_timestamp": "2026-11-23T01:00:00Z"},
    ]
    run_2 = [
        {"product_name": "Book A", "current_price": 42.0, "previous_price": 50.0, "price_change": -8.0, "run_timestamp": "2026-11-23T01:15:00Z"},
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        hist_path = os.path.join(tmpdir, "price_history.csv")

        # Run 1
        append_to_history(run_1, hist_path)
        latest_1 = load_latest_prices_from_history(hist_path)
        assert latest_1["Book A"] == 50.0

        # Run 2
        append_to_history(run_2, hist_path)
        latest_2 = load_latest_prices_from_history(hist_path)
        assert latest_2["Book A"] == 42.0

        # Verify file contains 2 rows (plus header = 3 lines)
        with open(hist_path, "r", encoding="utf-8") as fp:
            lines = [line.strip() for line in fp if line.strip()]
            assert len(lines) == 3
