from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://webscraper.io/test-sites/e-commerce/static/"
DEFAULT_PATHS = [
    "computers/laptops",
    "computers/tablets",
    "phones/touch",
]


def fetch_html(session: requests.Session, url: str) -> str:
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.text


def parse_product_cards(html: str, page_url: str) -> list[dict[str, object]]:
    soup = BeautifulSoup(html, "html.parser")
    products: list[dict[str, object]] = []
    parsed_path = urlparse(page_url).path.strip("/").split("/")
    category = parsed_path[3] if len(parsed_path) > 3 else ""
    subcategory = parsed_path[4] if len(parsed_path) > 4 else ""

    for index, card in enumerate(soup.select(".thumbnail"), start=1):
        title_tag = card.select_one(".title")
        price_tag = card.select_one(".price")
        description_tag = card.select_one(".description")
        reviews_tag = card.select_one(".ratings .pull-right")
        stars = len(card.select(".ratings span.ws-icon-star"))

        if title_tag is None or price_tag is None:
            continue

        relative_url = title_tag.get("href", "").strip()
        name = title_tag.get("title", "").strip() or title_tag.get_text(" ", strip=True)

        products.append(
            {
                "name": name,
                "price_text": price_tag.get_text(" ", strip=True),
                "description": description_tag.get_text(" ", strip=True) if description_tag else "",
                "reviews_text": reviews_tag.get_text(" ", strip=True) if reviews_tag else "0 reviews",
                "rating_stars": stars,
                "product_url": urljoin(page_url, relative_url),
                "page_url": page_url,
                "category": category,
                "subcategory": subcategory,
                "position_on_page": index,
            }
        )

    return products


def scrape_paths(paths: Iterable[str], delay: float = 1.0) -> list[dict[str, object]]:
    session = requests.Session()
    # Ignore broken proxy settings inherited from the local shell when possible.
    session.trust_env = False
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (compatible; MiniProjetBigData/1.0; +https://webscraper.io/test-sites/)"
        }
    )

    all_products: list[dict[str, object]] = []
    for path in paths:
        page_url = urljoin(BASE_URL, path)
        html = fetch_html(session, page_url)
        all_products.extend(parse_product_cards(html, page_url))
        time.sleep(delay)
    return all_products


def write_json(records: list[dict[str, object]], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def write_csv(records: list[dict[str, object]], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        target.write_text("", encoding="utf-8")
        return

    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scrape Web Scraper static e-commerce test site.")
    parser.add_argument(
        "--paths",
        nargs="+",
        default=DEFAULT_PATHS,
        help="Relative paths to scrape from the static e-commerce site.",
    )
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds.")
    parser.add_argument(
        "--json-output",
        default="data/raw/products_raw.json",
        help="Path of the raw JSON export.",
    )
    parser.add_argument(
        "--csv-output",
        default="data/raw/products_raw.csv",
        help="Path of the raw CSV export.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    records = scrape_paths(args.paths, delay=args.delay)
    write_json(records, Path(args.json_output))
    write_csv(records, Path(args.csv_output))
    print(f"Scraped {len(records)} products into {args.json_output} and {args.csv_output}.")


if __name__ == "__main__":
    main()
