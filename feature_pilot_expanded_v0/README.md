# Feature Pilot Expanded v0

This experiment expands the fresh detector pilot to 600 TextRich images: 50 real and 50 generated images in each of the six category cells. Detection uses the validated GPU `PP-OCRv5_server_det` output.

## Data and QA

- 600 manifest rows, 600 unique images
- 50 images per category-label cell
- 600/600 detector records successful
- 600 JSON outputs and 600 overlays present
- 42,642 valid OCR polygons
- 0 feature rows with NaN or infinity after the distance calculation fix

## Full-sample ablation

The 5-fold stratified nearest-centroid pilot produced these pooled balanced accuracies:

| Feature group | Mean balanced accuracy |
|---|---:|
| Quantity only | 0.720 |
| Arrangement only | 0.670 |
| Quantity + arrangement | 0.733 |

Within-category arrangement-only means ranged from 0.74 to 0.87. This is not enough to claim a universal layout pattern because pooled performance is lower and category-specific layout differences can drive within-category results.

## Density-matched check

Real/fake pairs were greedily matched within category by OCR region count. The strict subset keeps pairs whose absolute region-count difference is at most 10; the relaxed subset uses at most 20.

| Subset | Images | Quantity only | Arrangement only | Quantity + arrangement |
|---|---:|---:|---:|---:|
| Count difference <= 10 | 268 | 0.770 | 0.571 | 0.740 |
| Count difference <= 20 | 332 | 0.744 | 0.605 | 0.726 |

The arrangement-only score drops close to chance after text quantity is controlled. Some individual categories remain above chance, but the pooled result does not support a stable architecture- and category-independent arrangement signal yet.

## Leave-one-category-out check

Training on five categories and testing on the held-out category gave mean balanced accuracy of 0.602 for arrangement-only, 0.678 for quantity-only, and 0.682 for the combined group. On the count-difference <=10 subset, arrangement-only fell to 0.461, while quantity-only was 0.703. On the <=20 subset, arrangement-only was 0.488 and quantity-only was 0.669.

## Decision

**Needs revision before claiming a general non-semantic layout detector.** The pilot strongly supports continuing to separate quantity from arrangement. It does not currently support treating the arrangement-only signal as robust across the full dataset. The next defensible options are to narrow the thesis to category-conditional patterns, redesign the arrangement representation and test it with stricter source controls, or treat density/quantity as the primary finding.

The reproducible artifacts are `layout_features.csv`, `analysis/`, `analysis_density_le10/`, `analysis_density_le20/`, `analysis_loco/`, `analysis_loco_density_le10/`, and `analysis_loco_density_le20/`. The analysis implementations are `analyze_layout_pilot.py` and `analyze_leave_one_category_out.py`.

## 8x8 occupancy sensitivity check

The feature extractor was extended to include both 4x4 and 8x8 normalized center occupancy. On the full 600-image sample, the base arrangement features scored 0.692, 4x4-only arrangement scored 0.670, and 8x8-only arrangement scored 0.677. On the count-difference <=10 subset, base arrangement scored 0.579, 4x4-only scored 0.571, and 8x8-only scored 0.612. The finer grid improves the density-matched result somewhat, but it remains far from strong universal evidence and requires category-wise confirmation.
