import os
import sys
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from dotenv import load_dotenv

# Load secrets from .env safely (Step 6)
load_dotenv()

# Setup structured logging (Step 18)
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "price_tracker.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("PriceTracker")

HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "price_history.csv")
TARGET_DISCOUNT_THRESHOLD = 0.95  # Alert if price drops below 95% of previous price or target


def load_latest_prices_from_history(history_path: str = HISTORY_FILE) -> Dict[str, float]:
    """Loads the most recent price recorded for each product from price_history.csv."""
    if not os.path.exists(history_path):
        return {}
    try:
        df = pd.read_csv(history_path)
        if df.empty or "product_name" not in df.columns or "current_price" not in df.columns:
            return {}
        # Keep the latest record for each product
        latest_records = df.drop_duplicates(subset=["product_name"], keep="last")
        return dict(zip(latest_records["product_name"], latest_records["current_price"]))
    except Exception as e:
        logger.warning(f"Could not load previous price history: {e}")
        return {}


def compare_prices(
    scraped_records: List[Dict[str, Any]],
    previous_prices: Dict[str, float],
    custom_targets: Optional[Dict[str, float]] = None,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Compares newly scraped prices against historical records.

    Detects price drops and determines alert conditions.

    Returns:
        tuple: (all processed history entries, list of alert-triggered entries)
    """
    history_entries = []
    alerts = []
    now_iso = datetime.now(timezone.utc).isoformat()
    custom_targets = custom_targets or {}

    for item in scraped_records:
        name = item["product_name"]
        curr_price = float(item["price"])

        # Filter out false positives (e.g. £0.00 or corrupt scrape)
        if curr_price <= 0:
            logger.warning(f"Discarding invalid zero/negative price for '{name}'")
            continue

        prev_price = previous_prices.get(name, curr_price)
        price_change = round(curr_price - prev_price, 2)

        # Calculate percentage drop
        if prev_price > 0:
            price_drop_pct = round(((curr_price - prev_price) / prev_price) * 100, 2)
        else:
            price_drop_pct = 0.0

        # Define target price threshold
        target_price = custom_targets.get(name, round(prev_price * TARGET_DISCOUNT_THRESHOLD, 2))

        # Alert Condition: Real price drop detected OR dropped below target price
        alert_triggered = False
        alert_reason = ""

        if price_change < 0:
            alert_triggered = True
            alert_reason = f"Price dropped by £{abs(price_change):.2f} ({price_drop_pct}%)"
        elif curr_price < target_price:
            alert_triggered = True
            alert_reason = f"Price dropped below target threshold of £{target_price:.2f}"

        entry = {
            "product_name": name,
            "current_price": curr_price,
            "previous_price": prev_price,
            "price_change": price_change,
            "price_drop_pct": price_drop_pct,
            "target_price": target_price,
            "currency": item.get("currency", "GBP"),
            "url": item.get("url", ""),
            "availability": item.get("availability", "In Stock"),
            "alert_triggered": alert_triggered,
            "run_timestamp": now_iso,
        }
        history_entries.append(entry)

        if alert_triggered:
            entry_with_reason = dict(entry)
            entry_with_reason["alert_reason"] = alert_reason
            alerts.append(entry_with_reason)

    return history_entries, alerts


def append_to_history(entries: List[Dict[str, Any]], history_path: str = HISTORY_FILE) -> bool:
    """Appends newly checked records to price_history.csv without overwriting."""
    if not entries:
        return False
    try:
        os.makedirs(os.path.dirname(os.path.abspath(history_path)), exist_ok=True)
        df_new = pd.DataFrame(entries)

        file_exists = os.path.exists(history_path)
        df_new.to_csv(
            history_path,
            mode="a",
            header=not file_exists,
            index=False,
            encoding="utf-8",
        )
        logger.info(f"Appended {len(entries)} records to history file: {history_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to append to history: {e}")
        return False


def send_alerts(alerts: List[Dict[str, Any]]) -> int:
    """Delivers alerts via Console logging, Email (optional), and Telegram (optional)."""
    if not alerts:
        logger.info("No price drops detected on this scheduled cycle.")
        return 0

    logger.info("=" * 60)
    logger.info(f"🚨 PRICE DROP ALERT: {len(alerts)} PRODUCT(S) DROPPED IN PRICE!")
    logger.info("=" * 60)

    for a in alerts:
        msg = (
            f"🔔 [ALERT] '{a['product_name']}' dropped to £{a['current_price']:.2f} "
            f"(Previous: £{a['previous_price']:.2f} | Change: £{a['price_change']:.2f} / {a['price_drop_pct']}%)"
        )
        logger.warning(msg)

    # 1. Telegram Alert Dispatch (if configured in .env)
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if telegram_token and telegram_chat_id:
        try:
            import requests
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            text_body = f"🚨 *GlobalPay Price Tracker Alert*\n\n" + "\n".join(
                [f"• *{a['product_name']}*: £{a['current_price']} (was £{a['previous_price']})" for a in alerts]
            )
            resp = requests.post(telegram_url, json={"chat_id": telegram_chat_id, "text": text_body, "parse_mode": "Markdown"}, timeout=10)
            if resp.status_code == 200:
                logger.info("✓ Telegram alert notification delivered successfully.")
        except Exception as e:
            logger.error(f"Telegram dispatch failed: {e}")

    return len(alerts)


def run_tracker_cycle(
    max_pages: int = 2,
    history_path: str = HISTORY_FILE,
    custom_targets: Optional[Dict[str, float]] = None,
    simulated_price_drop: bool = False,
) -> Dict[str, Any]:
    """Executes a complete price tracking cycle: scrape -> compare -> alert -> append."""
    from scraper import scrape_books
    from cleaner import deduplicate_records

    logger.info("--- Starting Scheduled Price Tracker Cycle ---")

    # 1. Scrape latest live prices
    raw = scrape_books(max_pages=max_pages)
    clean, _ = deduplicate_records(raw)

    # If demo simulation requested, simulate a price drop on the first item for testing
    if simulated_price_drop and clean:
        clean[0]["price"] = round(clean[0]["price"] * 0.85, 2)  # 15% discount demo

    # 2. Load previous prices
    previous_prices = load_latest_prices_from_history(history_path)

    # 3. Compare prices
    history_entries, alerts = compare_prices(clean, previous_prices, custom_targets=custom_targets)

    # 4. Dispatch alerts
    alerts_count = send_alerts(alerts)

    # 5. Persist history
    append_to_history(history_entries, history_path)

    logger.info(f"Cycle finished. Tracked: {len(history_entries)} | Alerts Fired: {alerts_count}")
    return {
        "tracked_count": len(history_entries),
        "alerts_count": alerts_count,
        "alerts": alerts,
    }
