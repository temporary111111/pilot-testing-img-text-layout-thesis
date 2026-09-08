# Feature Pilot v0

This pilot uses the fresh 120-image detector QA manifest and the validated GPU output from `PP-OCRv5_server_det`.

## Population

- 6 categories
- 10 real (`label=0`) and 10 generated (`label=1`) images per category
- 120 images total, 60 per label
- 8,617 valid OCR polygons

## Feature groups

- `quantity_only`: region count, coverage, box-area summaries, box-size summaries, confidence summaries
- `arrangement_only`: normalized centers, spatial spread, nearest-neighbor and pairwise distances, alignment, orientation, and normalized 4x4 center occupancy
- `quantity_plus_arrangement`: both groups together

Features are extracted by `extract_layout_features.py`. The arrangement group intentionally excludes region count and area/coverage measures so the ablation addresses the thesis question directly.

## Preliminary result

The analysis uses a 5-fold stratified nearest-centroid classifier with standardization fitted inside each training fold. Pooled balanced accuracy was:

| Feature group | Mean balanced accuracy |
|---|---:|
| Quantity only | 0.700 |
| Arrangement only | 0.667 |
| Quantity + arrangement | 0.708 |

Within-category arrangement-only means ranged from 0.70 to 0.90 across the six categories, but each category has only 10 images per label and the pooled fold scores ranged from 0.583 to 0.750. These are feasibility signals, not final performance estimates.

## Density-control warning

Greedy real/fake matching by region count produced median absolute count differences from 4.5 to 26 regions by category. With a strict difference threshold of 10 regions, the category-level matched-pair counts were small (1 to 6 pairs). The current sample therefore cannot support a strong density-matched conclusion.

The next experiment should enlarge the balanced sample from the raw TextRich dataset, run the same validated detector, and select density-overlapping real/fake pairs within each category before testing arrangement-only features. The current pilot suggests a possible arrangement signal, but it may still reflect residual density, category-specific templates, or detector granularity.
