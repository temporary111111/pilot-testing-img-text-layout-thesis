"""Create a local, label-blind manual audit package for one category."""

from __future__ import annotations

import argparse
import csv
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--overlay-root", type=Path, required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--per-label", type=int, default=50)
    args = parser.parse_args()

    rows = [
        row
        for row in csv.DictReader(args.manifest.open(encoding="utf-8-sig", newline=""))
        if row["category"] == args.category
    ]
    selected = []
    for label in ("0", "1"):
        group = sorted((row for row in rows if row["label"] == label), key=lambda row: row["selection_score"])
        if len(group) < args.per_label:
            raise ValueError(f"{args.category} label {label} has only {len(group)} rows")
        selected.extend(group[: args.per_label])
    selected.sort(key=lambda row: (row["label"], row["selection_score"]))

    output = args.output_dir.resolve()
    image_dir = output / "images"
    overlay_dir = output / "overlays"
    image_dir.mkdir(parents=True, exist_ok=True)
    overlay_dir.mkdir(parents=True, exist_ok=True)
    blind = []
    key = []
    for index, row in enumerate(selected, start=1):
        audit_id = f"{args.category[:3].upper()}AUD_{index:03d}"
        source = args.dataset_root / Path(row["relative_path"])
        overlay = args.overlay_root / "PP-OCRv5_server_det" / f"{row['pilot_id']}.png"
        if not source.is_file():
            raise FileNotFoundError(source)
        if not overlay.is_file():
            raise FileNotFoundError(overlay)
        local_image = image_dir / f"{audit_id}{source.suffix}"
        local_overlay = overlay_dir / f"{audit_id}.png"
        shutil.copy2(source, local_image)
        shutil.copy2(overlay, local_overlay)
        blind.append(
            {
                "audit_id": audit_id,
                "pilot_id": row["pilot_id"],
                "local_image_path": str(local_image),
                "local_overlay_path": str(local_overlay),
                "box_fit_rating_1_to_5": "",
                "missed_text_rating_1_to_5": "",
                "false_nontext_box_rating_1_to_5": "",
                "fragmentation_rating_1_to_5": "",
                "rotation_fit_rating_1_to_5": "",
                "repeated_alignment_rating_1_to_5": "",
                "reviewer_notes": "",
            }
        )
        key.append(
            {
                "audit_id": audit_id,
                "pilot_id": row["pilot_id"],
                "category": row["category"],
                "label": row["label"],
                "relative_path": row["relative_path"],
            }
        )
    with (output / "blind_review.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=blind[0].keys())
        writer.writeheader()
        writer.writerows(blind)
    with (output / "answer_key.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=key[0].keys())
        writer.writeheader()
        writer.writerows(key)
    print(f"category={args.category}")
    print(f"selected={len(selected)}")
    print(f"images={len(list(image_dir.iterdir()))}")
    print(f"overlays={len(list(overlay_dir.iterdir()))}")


if __name__ == "__main__":
    main()
