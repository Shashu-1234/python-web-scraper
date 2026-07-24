"""Scrape quotes.toscrape.com and save the results as a CSV file."""

from __future__ import annotations

import argparse
import csv
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_START_URL = "https://quotes.toscrape.com/"
DEFAULT_OUTPUT_PATH = Path("data/output.csv")
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class Quote:
    """A quote record extracted from the website."""

    text: str
    author: str
    tags: tuple[str, ...]


def build_session() -> requests.Session:
    """Create an HTTP session with a timeout-friendly retry policy."""
    retry_policy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry_policy)
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "python-web-scraper/1.0 "
                "(educational project; contact: repository issues)"
            )
        }
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def parse_quotes(html: str) -> tuple[list[Quote], str | None]:
    """Parse quote records and the next-page link from an HTML document."""
    soup = BeautifulSoup(html, "html.parser")
    quotes: list[Quote] = []

    for item in soup.select("div.quote"):
        text_element = item.select_one("span.text")
        author_element = item.select_one("small.author")

        if text_element is None or author_element is None:
            LOGGER.warning("Skipping an incomplete quote record")
            continue

        tags = tuple(
            tag.get_text(strip=True) for tag in item.select("div.tags a.tag")
        )
        quotes.append(
            Quote(
                text=text_element.get_text(strip=True),
                author=author_element.get_text(strip=True),
                tags=tags,
            )
        )

    next_element = soup.select_one("li.next a")
    next_path = next_element.get("href") if next_element else None
    return quotes, str(next_path) if next_path else None


def scrape_quotes(
    start_url: str = DEFAULT_START_URL,
    max_pages: int | None = None,
    delay_seconds: float = 0.5,
    timeout_seconds: float = 15.0,
) -> list[Quote]:
    """Scrape quote records from one or more paginated pages."""
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be at least 1")
    if delay_seconds < 0:
        raise ValueError("delay_seconds cannot be negative")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than 0")

    session = build_session()
    current_url: str | None = start_url
    page_number = 0
    records: list[Quote] = []

    try:
        while current_url and (max_pages is None or page_number < max_pages):
            page_number += 1
            LOGGER.info("Scraping page %s: %s", page_number, current_url)

            response = session.get(current_url, timeout=timeout_seconds)
            response.raise_for_status()

            page_records, next_path = parse_quotes(response.text)
            records.extend(page_records)
            LOGGER.info("Collected %s records from page %s", len(page_records), page_number)

            current_url = urljoin(current_url, next_path) if next_path else None
            if current_url:
                time.sleep(delay_seconds)
    finally:
        session.close()

    return records


def write_csv(records: list[Quote], output_path: Path) -> None:
    """Write quote records to a UTF-8 CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=("quote", "author", "tags"))
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    "quote": record.text,
                    "author": record.author,
                    "tags": ", ".join(record.tags),
                }
            )


def parse_arguments() -> argparse.Namespace:
    """Read command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Scrape public quote data and save it as a CSV file."
    )
    parser.add_argument("--url", default=DEFAULT_START_URL, help="Starting page URL")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Destination CSV path",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages to scrape; the default scrapes all pages",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between requests in seconds",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Request timeout in seconds",
    )
    return parser.parse_args()


def main() -> int:
    """Run the command-line scraper."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    args = parse_arguments()

    try:
        records = scrape_quotes(
            start_url=args.url,
            max_pages=args.max_pages,
            delay_seconds=args.delay,
            timeout_seconds=args.timeout,
        )
        write_csv(records, args.output)
    except (requests.RequestException, OSError, ValueError) as error:
        LOGGER.error("Scraping failed: %s", error)
        return 1

    LOGGER.info("Saved %s records to %s", len(records), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
