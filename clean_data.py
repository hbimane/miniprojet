from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import urlparse


def load_records(source: Path) -> list[dict]:
    return json.loads(source.read_text(encoding="utf-8"))


def normalize_price(price_text: str) -> float:
    return float(price_text.replace("$", "").strip())


def normalize_reviews(reviews_text: str) -> int:
    match = re.search(r"(\d+)", reviews_text)
    return int(match.group(1)) if match else 0


def derive_category_fields(record: dict) -> tuple[str, str]:
    category = str(record.get("category", "")).strip().lower()
    subcategory = str(record.get("subcategory", "")).strip().lower()
    if category and subcategory:
        return category, subcategory

    path_parts = urlparse(record["page_url"]).path.strip("/").split("/")
    fallback_category = path_parts[3].lower() if len(path_parts) > 3 else category
    fallback_subcategory = path_parts[4].lower() if len(path_parts) > 4 else subcategory
    return fallback_category, fallback_subcategory


def clean_record(record: dict) -> dict:
    category, subcategory = derive_category_fields(record)
    return {
        "name": record["name"].strip(),
        "category": category,
        "subcategory": subcategory,
        "price": normalize_price(record["price_text"]),
        "reviews_count": normalize_reviews(record["reviews_text"]),
        "rating_stars": int(record["rating_stars"]),
        "description": " ".join(record["description"].split()),
        "product_url": record["product_url"],
        "page_url": record["page_url"],
        "position_on_page": int(record["position_on_page"]),
    }


def write_json(records: list[dict], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")


def write_jsonl(records: list[dict], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(record, ensure_ascii=False) for record in records]
    target.write_text("\n".join(lines), encoding="utf-8")


def write_csv(records: list[dict], target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not records:
        target.write_text("", encoding="utf-8")
        return

    with target.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clean scraped e-commerce records.")
    parser.add_argument("--input", default="data/raw/products_raw.json", help="Raw JSON file to clean.")
    parser.add_argument("--json-output", default="data/clean/products_clean.json", help="Clean JSON output.")
    parser.add_argument("--jsonl-output", default="data/clean/products_clean.jsonl", help="Clean JSONL output.")
    parser.add_argument("--csv-output", default="data/clean/products_clean.csv", help="Clean CSV output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_records = load_records(Path(args.input))
    clean_records = [clean_record(record) for record in raw_records]
    write_json(clean_records, Path(args.json_output))
    write_jsonl(clean_records, Path(args.jsonl_output))
    write_csv(clean_records, Path(args.csv_output))
    print(
        f"Cleaned {len(clean_records)} products into "
        f"{args.json_output}, {args.jsonl_output} and {args.csv_output}."
    )


if __name__ == "__main__":
    main()
