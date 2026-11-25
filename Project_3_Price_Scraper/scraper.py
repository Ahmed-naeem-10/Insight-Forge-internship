import urllib.parse
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from cleaner import clean_price, clean_availability, clean_text, clean_rating

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"


def fetch_page(
    url: str, session: Optional[requests.Session] = None, timeout: int = 15
) -> Optional[str]:
    """Fetches HTML content of a page with timeout and error handling.

    Returns the HTML string on success, or None if the request failed.
    """
    http = session or requests
    try:
        response = http.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
            },
        )
        if response.status_code == 200:
            # Explicitly decode as UTF-8 to prevent Â£ currency character corruption
            response.encoding = "utf-8"
            return response.text
        print(f"[Warning] HTTP {response.status_code} received for URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[Error] Failed to fetch {url}: {e}")
        return None


def parse_product_element(
    article: BeautifulSoup, current_page_url: str
) -> Optional[Dict[str, Any]]:
    """Extracts and normalizes product details from a single article.product_pod element."""
    try:
        # 1. Product Name (from <h3><a title="...">)
        h3_a = article.select_one("h3 a")
        if not h3_a:
            return None
        title = h3_a.get("title") or h3_a.get_text()
        product_name = clean_text(title)

        # 2. Product URL (absolute link)
        rel_href = h3_a.get("href", "")
        product_url = urllib.parse.urljoin(current_page_url, rel_href)

        # 3. Price
        price_elem = article.select_one(".price_color")
        raw_price = price_elem.get_text() if price_elem else None
        price = clean_price(raw_price)

        # 4. Availability
        avail_elem = article.select_one(".availability")
        raw_avail = avail_elem.get_text() if avail_elem else ""
        availability = clean_availability(raw_avail)

        # 5. Rating (Bonus Field)
        rating_elem = article.select_one(".star-rating")
        rating_classes = rating_elem.get("class", []) if rating_elem else []
        rating = clean_rating(rating_classes)

        # 6. Currency & Timestamp
        currency = "GBP"
        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "product_name": product_name,
            "price": price,
            "currency": currency,
            "url": product_url,
            "availability": availability,
            "timestamp": timestamp,
            "rating": rating,
        }
    except Exception as e:
        print(f"[Warning] Error parsing product element: {e}")
        return None


def scrape_books(
    max_pages: int = 3, start_url: str = START_URL
) -> List[Dict[str, Any]]:
    """Scrapes books across multiple paginated pages.

    Args:
        max_pages: Maximum number of pages to traverse (default: 3 = 60 products).
        start_url: URL of the first catalogue page.

    Returns:
        List of scraped book dictionaries.
    """
    scraped_items: List[Dict[str, Any]] = []
    current_url = start_url
    pages_crawled = 0

    session = requests.Session()

    while current_url and pages_crawled < max_pages:
        pages_crawled += 1
        print(f"[{pages_crawled}/{max_pages}] Fetching: {current_url}")
        html_content = fetch_page(current_url, session=session)

        if not html_content:
            print(f"[Error] Could not fetch page {pages_crawled}. Stopping crawl.")
            break

        soup = BeautifulSoup(html_content, "html.parser")
        articles = soup.select("article.product_pod")

        if not articles:
            print(f"[Notice] No product elements found on {current_url}.")
            break

        for art in articles:
            parsed = parse_product_element(art, current_url)
            if parsed and parsed.get("product_name") and parsed.get("price") is not None:
                scraped_items.append(parsed)

        # Pagination detection: check for next button
        next_button = soup.select_one("li.next a")
        if next_button and "href" in next_button.attrs:
            next_href = next_button["href"]
            current_url = urllib.parse.urljoin(current_url, next_href)
        else:
            current_url = None

    print(f"Crawling complete: {len(scraped_items)} records gathered across {pages_crawled} page(s).")
    return scraped_items
