from __future__ import annotations

import sys


def emit(category: str | None, count: int, price_sum: float, reviews_sum: int) -> None:
    if category is None or count == 0:
        return
    average_price = price_sum / count
    average_reviews = reviews_sum / count
    print(
        f"{category}\tcount={count}\tavg_price={average_price:.2f}\t"
        f"total_reviews={reviews_sum}\tavg_reviews={average_reviews:.2f}"
    )


def main() -> None:
    current_category: str | None = None
    count = 0
    price_sum = 0.0
    reviews_sum = 0

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        category, count_text, price_text, reviews_text = line.split("\t")
        record_count = int(count_text)
        price = float(price_text)
        reviews = int(reviews_text)

        if current_category is not None and category != current_category:
            emit(current_category, count, price_sum, reviews_sum)
            count = 0
            price_sum = 0.0
            reviews_sum = 0

        current_category = category
        count += record_count
        price_sum += price
        reviews_sum += reviews

    emit(current_category, count, price_sum, reviews_sum)


if __name__ == "__main__":
    main()
