"""Create a fresh, deterministic detector-validation manifest.

This intentionally does not read the previous pilot split or OCR artifacts.
It samples directly from the raw TextRich dataset.csv, taking 10 images from
each category x label cell (120 images total).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path


def score(relative_path: str) -> str:
    payload = f"DETECTOR_PILOT_V1|{relative_path}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--per-cell", type=int, default=10)
    args = parser.parse_args()

    dataset_root = args.dataset_root.resolve()
    manifest_path = dataset_root / "dataset.csv"
    rows = list(csv.DictReader(manifest_path.open("r", encoding="utf-8-sig", newline="")))

    cells: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        relative_path = row["image"].replace("\\", "/")
        image_path = dataset_root / Path(relative_path)
        if not image_path.is_file():
            raise FileNotFoundError(image_path)
        item = {
            "relative_path": relative_path,
            "category": row["category"],
            "label": row["label"],
            "score": score(relative_path),
        }
        cells[(row["category"], row["label"])].append(item)

    selected: list[dict[str, str]] = []
    for cell, items in sorted(cells.items()):
        if len(items) < args.per_cell:
            raise ValueError(f"Cell {cell} has only {len(items)} rows")
        selected.extend(sorted(items, key=lambda item: item["score"])[: args.per_cell])

    selected.sort(key=lambda item: item["score"])
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    full_rows = []
    blind_rows = []
    for index, item in enumerate(selected, start=1):
        pilot_id = f"DVP_{index:03d}_{item['score'][:12]}"
        full_rows.append(
            {
                "pilot_id": pilot_id,
                "relative_path": item["relative_path"],
                "category": item["category"],
                "label": item["label"],
                "selection_score": item["score"],
            }
        )
        blind_rows.append(
            {
                "pilot_id": pilot_id,
                "relative_path": item["relative_path"],
            }
        )

    with (output_dir / "detector_pilot_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=full_rows[0].keys())
        writer.writeheader()
        writer.writerows(full_rows)

    with (output_dir / "detector_pilot_blind_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=blind_rows[0].keys())
        writer.writeheader()
        writer.writerows(blind_rows)

    print(f"selected={len(selected)}")
    print(f"cells={len(cells)}")
    print(f"full_manifest={output_dir / 'detector_pilot_manifest.csv'}")
    print(f"blind_review={output_dir / 'detector_pilot_blind_review.csv'}")


if __name__ == "__main__":
    main()
