"""Leave-one-category-out check for the layout feature pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analyze_layout_pilot import feature_groups


def score(train: pd.DataFrame, test: pd.DataFrame, columns: list[str]) -> float:
    x_train = train[columns].to_numpy(dtype=float)
    x_test = test[columns].to_numpy(dtype=float)
    y_train = train.label.to_numpy(dtype=int)
    y_test = test.label.to_numpy(dtype=int)
    medians = np.nanmedian(x_train, axis=0)
    medians[~np.isfinite(medians)] = 0.0
    x_train = np.where(np.isfinite(x_train), x_train, medians)
    x_test = np.where(np.isfinite(x_test), x_test, medians)
    means = x_train.mean(axis=0)
    scales = x_train.std(axis=0)
    scales[scales < 1e-12] = 1.0
    x_train = (x_train - means) / scales
    x_test = (x_test - means) / scales
    centroids = np.vstack([x_train[y_train == label].mean(axis=0) for label in (0, 1)])
    predictions = ((x_test[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)
    recalls = []
    for label in (0, 1):
        mask = y_test == label
        recalls.append(float(np.mean(predictions[mask] == label)) if mask.any() else float("nan"))
    return float(np.nanmean(recalls))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--density-pairs", type=Path)
    parser.add_argument("--max-count-difference", type=int)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(args.features)
    if (args.density_pairs is None) != (args.max_count_difference is None):
        raise ValueError("--density-pairs and --max-count-difference must be supplied together")
    if args.density_pairs is not None:
        pairs = pd.read_csv(args.density_pairs)
        pairs = pairs[pairs.absolute_region_count_difference <= args.max_count_difference]
        selected_ids = set(pairs.real_id).union(set(pairs.fake_id))
        frame = frame[frame.pilot_id.isin(selected_ids)].copy()
    groups = feature_groups(frame.columns.tolist())
    rows = []
    for held_out in sorted(frame.category.unique()):
        train = frame[frame.category != held_out]
        test = frame[frame.category == held_out]
        for group_name, columns in groups.items():
            rows.append(
                {
                    "held_out_category": held_out,
                    "feature_group": group_name,
                    "balanced_accuracy": score(train, test, columns),
                    "train_images": len(train),
                    "test_images": len(test),
                    "features": len(columns),
                }
            )
    output = pd.DataFrame(rows)
    output.to_csv(args.output_dir / "leave_one_category_out.csv", index=False)
    means = output.groupby("feature_group", as_index=False).balanced_accuracy.mean()
    summary = {
        "features": str(args.features.resolve()),
        "images": int(len(frame)),
        "density_matching": args.max_count_difference,
        "mean_balanced_accuracy_by_feature_group": {row.feature_group: float(row.balanced_accuracy) for row in means.itertuples()},
        "caveat": "Leave-one-category-out is a generalization check, not a final model benchmark.",
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
