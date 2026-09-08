# Per-category 4x4 versus 8x8 comparison

The same nearest-centroid evaluation was run separately within each category. The density-matched subset keeps real/fake pairs with OCR region-count difference at most 10.

| Category | Full 4x4 | Full 8x8 | Matched <=10 4x4 | Matched <=10 8x8 |
|---|---:|---:|---:|---:|
| Academic posters | 0.83 | 0.80 | 0.64 | 0.82 |
| Commercial posters | 0.84 | 0.82 | 0.50 | 0.40 |
| Infographics | 0.74 | 0.74 | 0.69 | 0.74 |
| Receipts | 0.85 | 0.89 | 0.81 | 0.88 |
| Tables | 0.77 | 0.73 | 0.71 | 0.64 |
| UI screenshots | 0.87 | 0.82 | 0.73 | 0.80 |

## Interpretation

The 8x8 representation is category-dependent. It improves the density-matched result for academic posters, infographics, receipts, and UI screenshots, while it performs worse for commercial posters and tables. This is direct evidence that the useful spatial resolution depends on the visual category.

The result supports category-conditioned analysis and does not support selecting one occupancy resolution as universally best. The 8x8 representation should therefore be treated as a per-category sensitivity result, not as a universal replacement for 4x4.

The evaluation is exploratory: each matched category subset has a different number of images, and nearest-centroid scores are not final model benchmarks.
