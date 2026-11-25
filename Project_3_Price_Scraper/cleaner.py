import re
import html
from typing import List, Dict, Any, Optional, Tuple


def clean_price(raw_price: Any) -> Optional[float]:
    """Cleans raw price string and converts to numeric float.

    Handles currency symbols (£, Â£, $, €), whitespace, and comma decimal separators.
    Example: ' £51.77 ' -> 51.77, 'Â£12.99' -> 12.99
    """
    if raw_price is None:
        return None
    raw_str = str(raw_price).strip()
    # Match first valid numeric pattern with optional decimals
    match = re.search(r"(\d+(?:[.,]\d+)?)", raw_str)
    if not match:
        return None
    cleaned_num = match.group(1).replace(",", ".")
    try:
        return round(float(cleaned_num), 2)
    except ValueError:
        return None


def clean_availability(raw_text: Any) -> str:
    """Normalizes availability text into consistent 'In Stock' or 'Out of Stock'.

    Example: 'In stock (22 available)' -> 'In Stock'
    """
    if not raw_text:
        return "Out of Stock"
    text = str(raw_text).strip().lower()
    if "in stock" in text:
        return "In Stock"
    return "Out of Stock"


def clean_text(raw_text: Any) -> str:
    """Unescapes HTML entities, trims whitespace, and normalizes inner spaces."""
    if not raw_text:
        return ""
    unescaped = html.unescape(str(raw_text))
    # Replace multiple whitespaces/newlines with single space
    normalized = re.sub(r"\s+", " ", unescaped).strip()
    return normalized


def clean_rating(class_list: Any) -> str:
    """Extracts star rating from CSS classes.

    Example: ['star-rating', 'Three'] -> 'Three'
    """
    if not class_list:
        return "Not Rated"
    if isinstance(class_list, str):
        class_list = class_list.split()

    rating_map = {
        "one": "One",
        "two": "Two",
        "three": "Three",
        "four": "Four",
        "five": "Five",
    }
    for c in class_list:
        c_lower = c.strip().lower()
        if c_lower in rating_map:
            return rating_map[c_lower]
    return "Not Rated"


def deduplicate_records(
    records: List[Dict[str, Any]], key: str = "product_name"
) -> Tuple[List[Dict[str, Any]], int]:
    """Removes duplicate product records based on a unique identifier key.

    Returns:
        tuple: (list of unique records, count of dropped duplicate records)
    """
    seen = set()
    unique_records = []
    dropped_count = 0

    for item in records:
        val = item.get(key)
        identifier = str(val).strip().lower() if val is not None else None
        if not identifier or identifier in seen:
            dropped_count += 1
            continue
        seen.add(identifier)
        unique_records.append(item)

    return unique_records, dropped_count
