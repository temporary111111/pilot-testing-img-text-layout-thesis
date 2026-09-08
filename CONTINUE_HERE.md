# Thesis pilot continuation — 2026-09-08

## Current objective and user decisions

Determine whether non-semantic OCR-derived spatial layout provides repeatable
real/generated differences **within image categories**, while investigating text
quantity, detector errors and source/template differences. The user correctly
challenged the earlier assumption that the pattern must be universal. There is no
decision to reject the thesis or change its title. Cross-category transfer is an
extra diagnostic, not a pass/fail gate. Do not start final architectures yet.

## Saved work

- Proposal and earlier history: original proposal Markdown, `AI_HANDOFF.md`.
- Previous-work critique: `PREVIOUS_WORK_METHODOLOGY_AUDIT.md`.
- Detector scripts: `make_detector_pilot_manifest.py`, `run_detector_pilot.py`,
  `compare_detector_outputs.py`.
- Raw dataset (local only): `C:\Users\dev\Desktop\text-rich-ai-image-detector\data\TextRich`.
- Python: `.venv-ocr-gpu\Scripts\python.exe`, Python 3.11; RTX 3050 Laptop 4 GB.
- GPU packages reported during setup: Paddle GPU 3.3.0 (cu129), paddleocr 3.7.0,
  paddlex 3.7.2. NumPy, pandas and Shapely support the analysis; sklearn is absent.
- CPU environment is external to this repo, Paddle 3.3.1. CPU/GPU comparisons
  therefore compare environments as well as devices; they do not isolate hardware.
- `detector_crosscheck_v0`: 24-image CPU comparison of v5/v6.
- `detector_gpu_crosscheck_v0`: same 24 images on GPU. v5 coordinates identical;
  v6 max coordinate difference 2 px. Agreement is not detector accuracy.
- `detector_pilot_v0`: 120-image manifest. CPU outputs here are PARTIAL.
- `detector_pilot_gpu_v0`: complete 120-image v5 run, 8,617 regions.
- `detector_pilot_expanded_v0`: 600-image manifest, 50 per category/label cell.
- `detector_pilot_expanded_gpu_v0`: complete 600-image v5 run, 42,642 regions.
- `feature_pilot_v0`: initial 120-image exploratory analysis.
- `feature_pilot_expanded_v0`: 600-image features, count-matched subsets and
  leave-one-category-out diagnostics. 4x4/8x8 sensitivity outputs use suffixes
  `4x4_8x8`, and the direct group comparison uses `v2` output folders.

The repo includes polygon JSONs, metadata, manifests and feature tables so analysis
can be rerun without downloading images. Overlays and environments are ignored and
remain on the original PC. Visual review on another PC requires the raw dataset.

## What was actually tested

Nearest-centroid classifier; imputation and scaling fitted inside training folds;
one seed (20260908), five folds stratified by label. Pooled splits are not explicitly
stratified by category. Per-category tests fit a separate classifier for each category.
There are no repeated-split confidence intervals or label-permutation tests yet.

The 4x4 and 8x8 features count the fraction of **box centers** in image cells.
They do not encode full polygon occupancy or within-cell geometry. They are not OCR
input resolutions. Both representations also include 16 base arrangement statistics.
4x4 has 32 total features; 8x8 has 80. Finer is not automatically more accurate.

Historical mean fold balanced accuracies for count-difference <=10 pairs:

| Category | Images | Base + 4x4 | Base + 8x8 |
|---|---:|---:|---:|
| Academic posters | 50 | .640 | .820 |
| Commercial posters | 18 | .500 | .400 |
| Infographics | 54 | .687 | .740 |
| Receipts | 64 | .814 | .879 |
| Tables | 52 | .710 | .637 |
| UI screenshots | 30 | .733 | .800 |

These are observed exploratory scores, not established resolution differences.
Small unequal folds mean average fold accuracy is not exactly the accuracy of all
out-of-fold predictions. Do not choose a winner per category using these scores
and then report the same scores as an unbiased evaluation of that choice.

## Corrections to earlier conversation and reports

1. **OCR success is not localization validation.** Completeness was checked on
   600 records; visual spot-checks covered 12 representative 120-run overlays,
   plus earlier detector pairs. No full human ground-truth annotation exists.
2. **The group named `quantity_only` is not pure quantity.** It includes detector
   confidence, box dimensions and area statistics. Its scores cannot establish that
   text amount is the strongest signal. Keep confidence separate in the next version.
3. **Count matching is not full density control.** Existing greedy pairs match
   counts within category, not coverage, font size or OCR granularity. A tolerance
   of 10 boxes is large for a sparse poster. The subset changes the population;
   a score drop does not prove that quantity caused the original performance.
4. Existing matched evaluation splits images individually; matched partners are
   not held together in folds. Source/template and near-duplicate leakage were not
   ruled out. The 600-image sample includes the first 120, so it is not an independent
   confirmation. IDs can change when expanding; join runs by relative path.
5. Poor leave-one-category-out scores do not disprove useful within-category cues.
   No multiple-architecture claim has been tested by a nearest-centroid pilot.
6. Higher 8x8 scores in some categories are tentative, with no uncertainty analysis.
   Earlier wording such as 'direct evidence' or 'clearly category-dependent' was
   too strong. No final thesis decision should be based on those statements alone.

## Code caveats for the next analysis version

- `extract_layout_features.py` now emits `center_grid_4_r_c` and `center_grid_8_r_c`.
  Older CSVs use `center_grid_r_c`. Current `analyze_layout_pilot.py` silently filters
  missing columns; rerunning on old CSVs can omit occupancy columns and change the
  experiment. Add explicit schema checks/backward compatibility before such reruns.
- The duplicate-centroid zero-distance bug was fixed by excluding only the diagonal.
- Orientation currently uses the longest polygon edge and ordinary angle statistics.
  This can misrepresent short/tall text boxes and angles around +/-90 degrees.
- Extraction repairs invalid polygons and can truncate scores rather than preserving
  the exact original region-to-score mapping. Audit this before trusting new data.
- `run_detector_pilot.py` writes 'ok' for technical completion, and output folders
  must be fresh to avoid mixing runs. Preserve existing outputs.

## Next bounded work

The most recent user request is to commit/push this checkpoint with sufficient
context for another AI. After that, resume discussion before larger OCR runs.
Prioritize a versioned category-wise validation protocol: manual box QA with labels
hidden; confidence as a separate diagnostic; explicit count/coverage balance checks;
fixed paired/grouped folds; repeated split sensitivity and permutation checks.
Validate schema and feature calculations before reporting stronger conclusions.
Do not keep adding representations just to obtain better scores.

## Reproduction of the latest historical sensitivity analysis

From this repo with NumPy, pandas and Shapely installed:

```powershell
.\.venv-ocr-gpu\Scripts\python.exe .\analyze_layout_pilot.py --features .\feature_pilot_expanded_v0\layout_features_4x4_8x8.csv --output-dir .\reproduction_full
.\.venv-ocr-gpu\Scripts\python.exe .\analyze_layout_pilot.py --features .\feature_pilot_expanded_v0\layout_features_4x4_8x8.csv --output-dir .\reproduction_count_le10 --density-pairs .\feature_pilot_expanded_v0\analysis\density_matched_pairs.csv --max-count-difference 10
```

These commands reproduce the historical method; they do not resolve its caveats.
