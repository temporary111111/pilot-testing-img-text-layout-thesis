"""Compare two fresh detector outputs without treating agreement as ground truth."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from shapely.geometry import Polygon
from shapely.ops import unary_union


def load_record(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_polys(path: Path) -> list[Polygon]:
    record = load_record(path)
    return [Polygon(points) for points in record.get("polygons", [])]


def iou(a: Polygon, b: Polygon) -> float:
    if not a.is_valid or not b.is_valid or a.area <= 0 or b.area <= 0:
        return 0.0
    intersection = a.intersection(b).area
    union = a.union(b).area
    return float(intersection / union) if union else 0.0


def greedy_match(a: list[Polygon], b: list[Polygon], threshold: float) -> int:
    pairs = []
    for ia, pa in enumerate(a):
        for ib, pb in enumerate(b):
            value = iou(pa, pb)
            if value >= threshold:
                pairs.append((value, ia, ib))
    pairs.sort(reverse=True)
    used_a: set[int] = set()
    used_b: set[int] = set()
    matched = 0
    for _, ia, ib in pairs:
        if ia not in used_a and ib not in used_b:
            used_a.add(ia)
            used_b.add(ib)
            matched += 1
    return matched


def union_area(polys: list[Polygon]) -> float:
    valid = [p for p in polys if p.is_valid and p.area > 0]
    return float(unary_union(valid).area) if valid else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--model-a", default="PP-OCRv5_server_det")
    parser.add_argument("--model-b", default="PP-OCRv6_small_det")
    args = parser.parse_args()

    root = args.root.resolve()
    ids = [row["pilot_id"] for row in csv.DictReader((root / f"inventory_{args.model_a}.csv").open(encoding="utf-8"))]
    rows = []
    for pilot_id in ids:
        record_a = load_record(root / "json" / args.model_a / f"{pilot_id}.json")
        record_b = load_record(root / "json" / args.model_b / f"{pilot_id}.json")
        a = [Polygon(points) for points in record_a.get("polygons", [])]
        b = [Polygon(points) for points in record_b.get("polygons", [])]
        width = float(record_a["image_width"])
        height = float(record_a["image_height"])
        image_area = width * height
        row = {
            "pilot_id": pilot_id,
            "regions_a": len(a),
            "regions_b": len(b),
            "union_area_a_norm": union_area(a) / image_area,
            "union_area_b_norm": union_area(b) / image_area,
            "matches_iou_0_25": greedy_match(a, b, 0.25),
            "matches_iou_0_50": greedy_match(a, b, 0.50),
        }
        rows.append(row)

    summary = {
        "model_a": args.model_a,
        "model_b": args.model_b,
        "images": len(rows),
        "mean_regions_a": sum(r["regions_a"] for r in rows) / len(rows),
        "mean_regions_b": sum(r["regions_b"] for r in rows) / len(rows),
        "mean_union_area_a_norm": sum(r["union_area_a_norm"] for r in rows) / len(rows),
        "mean_union_area_b_norm": sum(r["union_area_b_norm"] for r in rows) / len(rows),
        "mean_matches_iou_0_25": sum(r["matches_iou_0_25"] for r in rows) / len(rows),
        "mean_matches_iou_0_50": sum(r["matches_iou_0_50"] for r in rows) / len(rows),
        "note": "Agreement is a robustness signal, not a ground-truth accuracy measure.",
        "per_image": rows,
    }
    (root / "detector_comparison.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in summary.items() if key != "per_image"}, indent=2))


if __name__ == "__main__":
    main()
