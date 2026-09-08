"""Extract non-semantic layout features from validated OCR polygons.

The script intentionally keeps quantity/density features separate from
arrangement features so the pilot can test whether arrangement carries signal
after text amount is controlled.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from shapely.geometry import Polygon
from shapely.ops import unary_union


QUANTITY_FEATURES = [
    "region_count",
    "union_coverage_norm",
    "sum_box_area_norm",
    "mean_box_area_norm",
    "median_box_area_norm",
    "std_box_area_norm",
    "mean_box_width_norm",
    "mean_box_height_norm",
    "mean_confidence",
    "low_confidence_fraction",
]

ARRANGEMENT_FEATURES = [
    "center_x_mean",
    "center_x_std",
    "center_y_mean",
    "center_y_std",
    "center_x_span",
    "center_y_span",
    "nearest_neighbor_mean_norm",
    "nearest_neighbor_median_norm",
    "nearest_neighbor_std_norm",
    "pairwise_distance_mean_norm",
    "pairwise_distance_std_norm",
    "row_alignment_fraction",
    "column_alignment_fraction",
    "angle_mean_abs_deg",
    "angle_std_deg",
    "rotated_fraction_gt_5deg",
]


def safe_stats(values: np.ndarray) -> tuple[float, float, float, float]:
    if values.size == 0:
        return float("nan"), float("nan"), float("nan"), float("nan")
    return (
        float(np.mean(values)),
        float(np.median(values)),
        float(np.std(values)),
        float(np.max(values) - np.min(values)),
    )


def normalize_angle_degrees(angle: float) -> float:
    """Map an undirected line orientation to [-90, 90)."""
    value = (angle + 90.0) % 180.0 - 90.0
    return float(value)


def polygon_properties(points: list[list[float]]) -> tuple[Polygon, dict[str, float]] | None:
    try:
        polygon = Polygon(points)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty or polygon.area <= 0:
            return None
        coords = np.asarray(points, dtype=float)
        if coords.shape[0] < 4:
            return None
        edges = np.roll(coords, -1, axis=0) - coords
        lengths = np.linalg.norm(edges, axis=1)
        longest = int(np.argmax(lengths))
        vector = edges[longest]
        angle = normalize_angle_degrees(math.degrees(math.atan2(vector[1], vector[0])))
        min_xy = coords.min(axis=0)
        max_xy = coords.max(axis=0)
        return polygon, {
            "area": float(polygon.area),
            "width": float(max_xy[0] - min_xy[0]),
            "height": float(max_xy[1] - min_xy[1]),
            "angle_deg": angle,
            "center_x": float(polygon.centroid.x),
            "center_y": float(polygon.centroid.y),
        }
    except Exception:
        return None


def union_area(polygons: list[Polygon]) -> float:
    valid = [p for p in polygons if not p.is_empty and p.is_valid and p.area > 0]
    return float(unary_union(valid).area) if valid else 0.0


def extract_record(manifest_row: dict[str, str], ocr_path: Path) -> tuple[dict, int]:
    record = json.loads(ocr_path.read_text(encoding="utf-8"))
    if record.get("status") != "ok":
        raise RuntimeError(f"OCR record is not ok: {record.get('error')}")
    width = float(record["image_width"])
    height = float(record["image_height"])
    image_area = width * height
    polygons: list[Polygon] = []
    props: list[dict[str, float]] = []
    for points in record.get("polygons", []):
        item = polygon_properties(points)
        if item is not None:
            polygon, values = item
            polygons.append(polygon)
            props.append(values)
    scores = np.asarray(record.get("scores", []), dtype=float)
    if scores.size != len(props):
        scores = scores[: len(props)]
    count = len(props)
    areas = np.asarray([p["area"] / image_area for p in props], dtype=float)
    widths = np.asarray([p["width"] / width for p in props], dtype=float)
    heights = np.asarray([p["height"] / height for p in props], dtype=float)
    xs = np.asarray([p["center_x"] / width for p in props], dtype=float)
    ys = np.asarray([p["center_y"] / height for p in props], dtype=float)
    angles = np.asarray([p["angle_deg"] for p in props], dtype=float)

    if count >= 2:
        centers = np.column_stack([xs, ys])
        distances = np.sqrt(((centers[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2))
        # Exclude only self-distances. Distinct boxes can share a centroid;
        # those are valid zero-distance observations rather than infinities.
        np.fill_diagonal(distances, np.inf)
        nearest = distances.min(axis=1)
        tri = distances[np.triu_indices(count, k=1)]
        nearest_mean, nearest_median, nearest_std, _ = safe_stats(nearest)
        pair_mean, _, pair_std, _ = safe_stats(tri)
        y_diff = np.abs(ys[:, None] - ys[None, :])
        x_diff = np.abs(xs[:, None] - xs[None, :])
        upper = np.triu_indices(count, k=1)
        row_alignment = float(np.mean(y_diff[upper] <= 0.02))
        column_alignment = float(np.mean(x_diff[upper] <= 0.02))
    else:
        nearest_mean = nearest_median = nearest_std = pair_mean = pair_std = float("nan")
        row_alignment = column_alignment = float("nan")

    def grid_fractions(values_x: np.ndarray, values_y: np.ndarray) -> dict[str, float]:
        output = {}
        for size in (4, 8):
            if count == 0:
                for row in range(size):
                    for col in range(size):
                        output[f"center_grid_{size}_{row}_{col}"] = 0.0
                continue
            cols = np.minimum((values_x * size).astype(int), size - 1)
            rows = np.minimum((values_y * size).astype(int), size - 1)
            for row in range(size):
                for col in range(size):
                    output[f"center_grid_{size}_{row}_{col}"] = float(np.mean((rows == row) & (cols == col)))
        return output

    mean_area, median_area, std_area, _ = safe_stats(areas)
    mean_width, _, _, _ = safe_stats(widths)
    mean_height, _, _, _ = safe_stats(heights)
    mean_angle, _, std_angle, _ = safe_stats(angles)
    confidence_mean = float(np.mean(scores)) if scores.size else float("nan")
    low_conf_fraction = float(np.mean(scores < 0.75)) if scores.size else float("nan")
    result = {
        "pilot_id": manifest_row["pilot_id"],
        "relative_path": manifest_row["relative_path"],
        "category": manifest_row["category"],
        "label": int(manifest_row["label"]),
        "image_width": int(width),
        "image_height": int(height),
        "region_count": count,
        "union_coverage_norm": union_area(polygons) / image_area,
        "sum_box_area_norm": float(areas.sum()) if count else 0.0,
        "mean_box_area_norm": mean_area,
        "median_box_area_norm": median_area,
        "std_box_area_norm": std_area,
        "mean_box_width_norm": mean_width,
        "mean_box_height_norm": mean_height,
        "mean_confidence": confidence_mean,
        "low_confidence_fraction": low_conf_fraction,
        "center_x_mean": float(np.mean(xs)) if count else float("nan"),
        "center_x_std": float(np.std(xs)) if count else float("nan"),
        "center_y_mean": float(np.mean(ys)) if count else float("nan"),
        "center_y_std": float(np.std(ys)) if count else float("nan"),
        "center_x_span": float(xs.max() - xs.min()) if count else float("nan"),
        "center_y_span": float(ys.max() - ys.min()) if count else float("nan"),
        "nearest_neighbor_mean_norm": nearest_mean if count >= 2 else float("nan"),
        "nearest_neighbor_median_norm": nearest_median if count >= 2 else float("nan"),
        "nearest_neighbor_std_norm": nearest_std if count >= 2 else float("nan"),
        "pairwise_distance_mean_norm": pair_mean if count >= 2 else float("nan"),
        "pairwise_distance_std_norm": pair_std if count >= 2 else float("nan"),
        "row_alignment_fraction": row_alignment,
        "column_alignment_fraction": column_alignment,
        "angle_mean_abs_deg": float(np.mean(np.abs(angles))) if count else float("nan"),
        "angle_std_deg": std_angle,
        "rotated_fraction_gt_5deg": float(np.mean(np.abs(angles) > 5.0)) if count else float("nan"),
        "ocr_runtime_seconds": float(record.get("runtime_seconds", float("nan"))),
    }
    result.update(grid_fractions(xs, ys))
    # Distances above are measured in normalized center coordinates already.
    return result, count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--ocr-dir", type=Path, required=True)
    parser.add_argument("--model-name", default="PP-OCRv5_server_det")
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--metadata-json", type=Path, required=True)
    args = parser.parse_args()

    manifest_rows = list(csv.DictReader(args.manifest.open(encoding="utf-8-sig", newline="")))
    records = []
    valid_counts = []
    for row in manifest_rows:
        path = args.ocr_dir / f"{row['pilot_id']}.json"
        record, valid_count = extract_record(row, path)
        records.append(record)
        valid_counts.append(valid_count)
    frame = pd.DataFrame(records)
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_csv, index=False)
    metadata = {
        "script": "extract_layout_features.py",
        "manifest": str(args.manifest.resolve()),
        "ocr_dir": str(args.ocr_dir.resolve()),
        "model_name": args.model_name,
        "images": len(records),
        "total_valid_polygons": int(sum(valid_counts)),
        "quantity_features": QUANTITY_FEATURES,
        "arrangement_features": ARRANGEMENT_FEATURES + [
            f"center_grid_{size}_{row}_{col}"
            for size in (4, 8)
            for row in range(size)
            for col in range(size)
        ],
        "note": "Arrangement features are intentionally separated from text quantity/density features for ablation.",
    }
    args.metadata_json.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps({key: metadata[key] for key in ("images", "total_valid_polygons", "model_name")}, indent=2))


if __name__ == "__main__":
    main()
