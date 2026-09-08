"""Run an auditable feasibility analysis on extracted OCR layout features.

This is deliberately a small, interpretable pilot. It reports within-category
effect sizes and a nearest-centroid cross-validation score for quantity-only,
arrangement-only, and combined features. It is not the final thesis model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def feature_groups(columns: list[str]) -> dict[str, list[str]]:
    quantity = [
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
    arrangement = [
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
    ] + [
        f"center_grid_{size}_{row}_{col}"
        for size in (4, 8)
        for row in range(size)
        for col in range(size)
    ]
    base_arrangement = [name for name in arrangement if not name.startswith("center_grid_")]
    grid_4 = [f"center_grid_4_{row}_{col}" for row in range(4) for col in range(4)]
    grid_8 = [f"center_grid_8_{row}_{col}" for row in range(8) for col in range(8)]
    groups = {
        "quantity_only": [name for name in quantity if name in columns],
        "arrangement_only": [name for name in arrangement if name in columns],
        "arrangement_base_only": [name for name in base_arrangement if name in columns],
        "arrangement_4x4_only": [name for name in base_arrangement + grid_4 if name in columns],
        "arrangement_8x8_only": [name for name in base_arrangement + grid_8 if name in columns],
    }
    groups["quantity_plus_arrangement"] = groups["quantity_only"] + groups["arrangement_only"]
    return groups


def cohen_d(values0: np.ndarray, values1: np.ndarray) -> float:
    values0 = values0[np.isfinite(values0)]
    values1 = values1[np.isfinite(values1)]
    if len(values0) < 2 or len(values1) < 2:
        return float("nan")
    variance0 = np.var(values0, ddof=1)
    variance1 = np.var(values1, ddof=1)
    pooled = math_sqrt_safe(((len(values0) - 1) * variance0 + (len(values1) - 1) * variance1) / (len(values0) + len(values1) - 2))
    return float((np.mean(values1) - np.mean(values0)) / pooled) if pooled > 0 else 0.0


def math_sqrt_safe(value: float) -> float:
    return float(np.sqrt(max(float(value), 0.0)))


def make_folds(labels: np.ndarray, folds: int, seed: int) -> np.ndarray:
    assignments = np.full(len(labels), -1, dtype=int)
    rng = np.random.default_rng(seed)
    for label in (0, 1):
        indices = np.flatnonzero(labels == label)
        shuffled = indices[rng.permutation(len(indices))]
        for position, index in enumerate(shuffled):
            assignments[index] = position % folds
    return assignments


def nearest_centroid_cv(frame: pd.DataFrame, columns: list[str], folds: int, seed: int) -> list[float]:
    values = frame[columns].to_numpy(dtype=float)
    labels = frame["label"].to_numpy(dtype=int)
    fold_ids = make_folds(labels, folds, seed)
    scores: list[float] = []
    for fold in range(folds):
        train = fold_ids != fold
        test = fold_ids == fold
        if not test.any() or len(np.unique(labels[train])) < 2:
            continue
        train_values = values[train].copy()
        test_values = values[test].copy()
        medians = np.nanmedian(train_values, axis=0)
        medians[~np.isfinite(medians)] = 0.0
        train_values = np.where(np.isfinite(train_values), train_values, medians)
        test_values = np.where(np.isfinite(test_values), test_values, medians)
        means = train_values.mean(axis=0)
        scales = train_values.std(axis=0)
        scales[scales < 1e-12] = 1.0
        train_values = (train_values - means) / scales
        test_values = (test_values - means) / scales
        centroids = np.vstack([train_values[labels[train] == label].mean(axis=0) for label in (0, 1)])
        distances = ((test_values[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
        predictions = distances.argmin(axis=1)
        true = labels[test]
        recalls = []
        for label in (0, 1):
            mask = true == label
            recalls.append(float(np.mean(predictions[mask] == label)) if mask.any() else float("nan"))
        scores.append(float(np.nanmean(recalls)))
    return scores


def density_pairs(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for category, group in frame.groupby("category", sort=True):
        real = group[group.label == 0].copy()
        fake = group[group.label == 1].copy()
        candidates = []
        for real_index, real_row in real.iterrows():
            for fake_index, fake_row in fake.iterrows():
                difference = abs(int(real_row.region_count) - int(fake_row.region_count))
                candidates.append((difference, real_index, fake_index))
        candidates.sort(key=lambda item: (item[0], str(item[1]), str(item[2])))
        used_real: set[int] = set()
        used_fake: set[int] = set()
        for difference, real_index, fake_index in candidates:
            if real_index in used_real or fake_index in used_fake:
                continue
            used_real.add(real_index)
            used_fake.add(fake_index)
            real_row = real.loc[real_index]
            fake_row = fake.loc[fake_index]
            rows.append(
                {
                    "category": category,
                    "real_id": real_row.pilot_id,
                    "fake_id": fake_row.pilot_id,
                    "real_region_count": int(real_row.region_count),
                    "fake_region_count": int(fake_row.region_count),
                    "absolute_region_count_difference": int(difference),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--features", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=20260908)
    parser.add_argument("--density-pairs", type=Path, help="Existing greedy pair CSV used to select a matched subset")
    parser.add_argument("--max-count-difference", type=int, help="Keep only pair rows at or below this region-count difference")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(args.features)
    subset_metadata = {"density_matching_applied": False}
    if args.density_pairs is not None or args.max_count_difference is not None:
        if args.density_pairs is None or args.max_count_difference is None:
            raise ValueError("--density-pairs and --max-count-difference must be supplied together")
        pair_frame = pd.read_csv(args.density_pairs)
        selected_pairs = pair_frame[pair_frame["absolute_region_count_difference"] <= args.max_count_difference]
        selected_ids = set(selected_pairs["real_id"]).union(set(selected_pairs["fake_id"]))
        before = len(frame)
        frame = frame[frame["pilot_id"].isin(selected_ids)].copy()
        subset_metadata = {
            "density_matching_applied": True,
            "density_pairs_source": str(args.density_pairs.resolve()),
            "max_count_difference": args.max_count_difference,
            "selected_pairs": int(len(selected_pairs)),
            "selected_images": int(len(frame)),
            "images_before_filter": before,
        }
    groups = feature_groups(frame.columns.tolist())

    effect_rows = []
    for scope_name, scope in [("pooled", frame)] + [(str(category), group) for category, group in frame.groupby("category", sort=True)]:
        for group_name, columns in groups.items():
            for feature in columns:
                values0 = scope.loc[scope.label == 0, feature].to_numpy(dtype=float)
                values1 = scope.loc[scope.label == 1, feature].to_numpy(dtype=float)
                effect_rows.append(
                    {
                        "scope": scope_name,
                        "feature_group": group_name,
                        "feature": feature,
                        "real_mean": float(np.nanmean(values0)),
                        "fake_mean": float(np.nanmean(values1)),
                        "cohen_d_fake_minus_real": cohen_d(values0, values1),
                        "absolute_cohen_d": abs(cohen_d(values0, values1)),
                    }
                )
    pd.DataFrame(effect_rows).to_csv(args.output_dir / "effect_sizes_by_category.csv", index=False)

    cv_rows = []
    for scope_name, scope in [("pooled", frame)] + [(str(category), group) for category, group in frame.groupby("category", sort=True)]:
        for group_name, columns in groups.items():
            scores = nearest_centroid_cv(scope.reset_index(drop=True), columns, args.folds, args.seed)
            for fold_number, score in enumerate(scores, start=1):
                cv_rows.append(
                    {
                        "scope": scope_name,
                        "feature_group": group_name,
                        "fold": fold_number,
                        "balanced_accuracy": score,
                        "images": len(scope),
                        "features": len(columns),
                    }
                )
            cv_rows.append(
                {
                    "scope": scope_name,
                    "feature_group": group_name,
                    "fold": "mean",
                    "balanced_accuracy": float(np.mean(scores)) if scores else float("nan"),
                    "images": len(scope),
                    "features": len(columns),
                }
            )
    pd.DataFrame(cv_rows).to_csv(args.output_dir / "nearest_centroid_cv.csv", index=False)

    pairs = density_pairs(frame)
    pairs.to_csv(args.output_dir / "density_matched_pairs.csv", index=False)
    match_summary = (
        pairs.groupby("category", as_index=False)["absolute_region_count_difference"]
        .agg(["count", "mean", "median", "max"])
        .reset_index()
        .rename(columns={"count": "pairs", "mean": "mean_abs_count_difference", "median": "median_abs_count_difference", "max": "max_abs_count_difference"})
    )
    match_summary.to_csv(args.output_dir / "density_match_summary.csv", index=False)

    effect = pd.DataFrame(effect_rows)
    cv = pd.DataFrame(cv_rows)
    summary = {
        "features": str(args.features.resolve()),
        "images": int(len(frame)),
        "categories": sorted(frame.category.unique().tolist()),
        "label_counts": {str(key): int(value) for key, value in frame.label.value_counts().sort_index().items()},
        "feature_groups": groups,
        **subset_metadata,
        "cross_validation": "5-fold stratified nearest-centroid; standardization fitted within each training fold",
        "pooled_cv_mean_balanced_accuracy": {
            group: float(cv[(cv.scope == "pooled") & (cv.feature_group == group) & (cv.fold == "mean")].balanced_accuracy.iloc[0])
            for group in groups
        },
        "top_within_category_effects": effect[effect.scope != "pooled"].sort_values("absolute_cohen_d", ascending=False).head(20).to_dict(orient="records"),
        "density_match_summary": match_summary.to_dict(orient="records"),
        "caveat": "This is a feasibility pilot, not a final performance estimate or detector-accuracy benchmark.",
    }
    (args.output_dir / "pilot_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps({"images": len(frame), "pooled_cv_mean_balanced_accuracy": summary["pooled_cv_mean_balanced_accuracy"]}, indent=2))


if __name__ == "__main__":
    main()
