import os
import json
from typing import List, Dict, Any, Optional
import pandas as pd

COLUMNS_ORDER = [
    "product_name",
    "price",
    "currency",
    "url",
    "availability",
    "timestamp",
    "rating",
]


def save_to_csv(records: List[Dict[str, Any]], filepath: str) -> bool:
    """Exports records list to a structured CSV file."""
    if not records:
        print("[Warning] No records provided to save_to_csv.")
        return False
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        df = pd.DataFrame(records)
        # Ensure standard column ordering
        existing_cols = [c for c in COLUMNS_ORDER if c in df.columns]
        extra_cols = [c for c in df.columns if c not in COLUMNS_ORDER]
        df = df[existing_cols + extra_cols]
        df.to_csv(filepath, index=False, encoding="utf-8")
        print(f"✓ Saved {len(df)} records to CSV: {filepath}")
        return True
    except Exception as e:
        print(f"[Error] Failed to save CSV to {filepath}: {e}")
        return False


def save_to_json(records: List[Dict[str, Any]], filepath: str, indent: int = 2) -> bool:
    """Exports records list to a formatted JSON file."""
    if not records:
        print("[Warning] No records provided to save_to_json.")
        return False
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=indent, ensure_ascii=False)
        print(f"✓ Saved {len(records)} records to JSON: {filepath}")
        return True
    except Exception as e:
        print(f"[Error] Failed to save JSON to {filepath}: {e}")
        return False


def load_from_csv(filepath: str) -> List[Dict[str, Any]]:
    """Loads records from an existing CSV file."""
    if not os.path.exists(filepath):
        print(f"[Warning] File not found: {filepath}")
        return []
    try:
        df = pd.read_csv(filepath)
        return df.to_dict(orient="records")
    except Exception as e:
        print(f"[Error] Failed to load CSV from {filepath}: {e}")
        return []


def load_from_json(filepath: str) -> List[Dict[str, Any]]:
    """Loads records from an existing JSON file."""
    if not os.path.exists(filepath):
        print(f"[Warning] File not found: {filepath}")
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to load JSON from {filepath}: {e}")
        return []


def validate_dataset(filepath: str) -> Dict[str, Any]:
    """Validates the saved dataset against completeness and quality standards."""
    if not os.path.exists(filepath):
        return {"exists": False, "error": "File does not exist"}
    try:
        df = pd.read_csv(filepath) if filepath.endswith(".csv") else pd.read_json(filepath)
        total_rows = len(df)
        missing_values = df.isnull().sum().to_dict()
        duplicates = int(df.duplicated(subset=["product_name"]).sum())
        non_numeric_prices = int((~pd.to_numeric(df["price"], errors="coerce").notnull()).sum())

        return {
            "exists": True,
            "total_records": total_rows,
            "missing_values": missing_values,
            "duplicate_titles": duplicates,
            "invalid_prices": non_numeric_prices,
            "columns": list(df.columns),
            "is_valid": total_rows >= 20 and duplicates == 0 and non_numeric_prices == 0,
        }
    except Exception as e:
        return {"exists": False, "error": str(e)}
