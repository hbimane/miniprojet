from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def run_step(command: list[str], stdout_path: Path | None = None) -> None:
    if stdout_path is None:
        subprocess.run(command, check=True)
        return

    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    with stdout_path.open("w", encoding="utf-8") as handle:
        subprocess.run(command, check=True, stdout=handle)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the full local scraping and MapReduce pipeline.")
    parser.add_argument("--python", default=shutil.which("python") or "python", help="Python executable to use.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    python_cmd = args.python

    run_step([python_cmd, "scraper.py"])
    run_step([python_cmd, "clean_data.py"])

    cleaned_path = Path("data/clean/products_clean.jsonl")
    mapped_path = Path("data/mapreduce/mapped.txt")
    sorted_path = Path("data/mapreduce/mapped_sorted.txt")
    reduced_path = Path("data/mapreduce/reduced.txt")
    mapped_path.parent.mkdir(parents=True, exist_ok=True)

    with cleaned_path.open("r", encoding="utf-8") as input_handle, mapped_path.open("w", encoding="utf-8") as mapped:
        subprocess.run([python_cmd, "mapper.py"], stdin=input_handle, stdout=mapped, check=True)

    sorted_path.write_text("\n".join(sorted(mapped_path.read_text(encoding="utf-8").splitlines())), encoding="utf-8")

    with sorted_path.open("r", encoding="utf-8") as mapped_sorted, reduced_path.open("w", encoding="utf-8") as reduced:
        subprocess.run([python_cmd, "reducer.py"], stdin=mapped_sorted, stdout=reduced, check=True)

    print("Pipeline completed successfully.")
    print(f"Reducer output available in {reduced_path}")


if __name__ == "__main__":
    main()
