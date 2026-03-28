from __future__ import annotations

import json
import sys


def main() -> None:
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        record = json.loads(line)
        category = record["category"]
        price = float(record["price"])
        reviews_count = int(record["reviews_count"])
        print(f"{category}\t1\t{price}\t{reviews_count}")


if __name__ == "__main__":
    main()
