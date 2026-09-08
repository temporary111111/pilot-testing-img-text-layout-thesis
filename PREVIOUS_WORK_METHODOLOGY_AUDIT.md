# Independent Methodology Audit of the Existing Pilot Work

**Audit date:** 2026-09-07  
**Primary question:** Does non-semantic OCR-derived text layout contain a stable pattern that helps distinguish real from AI-generated text-rich images?  
**Data inspected:** Local TextRich dataset and existing train/validation artifacts. The TEST image files were not opened or processed.

## Overall assessment: Needs revision before hypothesis testing

The existing work provides a useful and unusually well-documented engineering foundation: the dataset was audited, exact and near-duplicate controls were applied, the pilot is balanced by category and class, the split is frozen, OCR recognition is excluded, OCR outputs preserve quadrilateral polygons, and the layout artifacts are reproducible.

However, the current methodology is not yet sufficient to conclude that a genuine **spatial-layout pattern** exists. The largest risks are that a future classifier could learn text quantity, OCR segmentation behavior, density-group class imbalance, category composition, or source-dataset conventions instead of spatial arrangement.

The frozen artifacts should be preserved for provenance. Methodological decisions may be revised through a new, explicitly versioned pilot protocol.

## Question and claim being validated

The immediate feasibility question should be:

> Within the TextRich pilot, do non-semantic OCR-derived spatial-arrangement cues contain reproducible authenticity-related signal after separating them from text quantity, OCR detector behavior, image category, and density composition?

This is narrower and more testable than claiming that AI-generated images have a universal text-layout signature.

## Verified strengths

1. The manifest contains 12,095 existing image files: 5,986 Real and 6,109 Generated.
2. The frozen pilot contains 2,400 images with exactly 200 Real and 200 Generated per category.
3. Split counts are internally consistent: 1,680 TRAIN, 360 validation, and 360 TEST.
4. Exact duplicates and selected pHash near-duplicate clusters were controlled before sampling.
5. OCR extraction used text detection only; recognized words were not stored.
6. TRAIN+validation OCR inventory contains 2,040 samples, matching the split counts.
7. Existing OCR outputs use four-point polygons and passed structural checks for finite, in-bounds coordinates.
8. B1 and B2 artifact row counts match the TRAIN and validation splits.
9. B1 has an explicit 16-feature whitelist, reducing accidental target or metadata leakage.
10. Density thresholds were derived from TRAIN only.
11. Existing reports preserve configuration, package, model, and artifact fingerprints.

## Issues found

### 1. High severity: OCR technical success is not OCR localization accuracy

The current OCR audits prove that the program ran and produced structurally valid polygons. They do not measure whether:

- all visible text was detected;
- non-text regions were falsely detected;
- polygons tightly fit the text;
- rotated text angles are correct;
- errors differ between Real and Generated images.

Five existing overlays were inspected informally and showed generally tight boxes, including a rotated quadrilateral around one slanted UI word. Five images are not enough for an accuracy claim.

**Impact:** A classifier may learn class-dependent OCR failures or segmentation differences instead of layout.

**Required correction:** Perform a blinded, balanced manual OCR-quality audit before interpreting layout classification results.

### 2. High severity: text quantity is mixed with spatial arrangement

The frozen B1 representation includes `num_regions` and `text_coverage_ratio`. B2 occupancy also reflects how much text is present. A successful layout-only classifier may therefore rely only on the amount of detected text rather than its spatial arrangement.

TRAIN descriptive summaries already show systematic count differences. Generated images have higher mean region counts in all six categories, although coverage differences change direction by category. Examples:

| Category | Generated mean regions | Real mean regions | Generated mean coverage | Real mean coverage |
|---|---:|---:|---:|---:|
| Academic Posters | 197.75 | 162.39 | 0.2366 | 0.2881 |
| Commercial Posters | 23.06 | 7.46 | 0.1600 | 0.1197 |
| Infographic Charts | 58.03 | 32.83 | 0.1648 | 0.1850 |
| Receipts | 54.29 | 52.59 | 0.2192 | 0.2658 |
| Tables | 127.77 | 77.69 | 0.2886 | 0.3110 |
| UI Screenshots | 43.05 | 19.28 | 0.1224 | 0.1062 |

These differences may reflect actual design, OCR splitting behavior, or both.

**Impact:** “Layout contains signal” could mean only “the detector returns more boxes.”

**Required correction:** Use explicit ablations:

- quantity-only: region count and coverage;
- box-size/shape summaries;
- position/spacing features excluding count and coverage;
- complete B1;
- B2 polygon map.

### 3. High severity: global density groups are confounded with class and category

The TRAIN q33/q67 thresholds create equal-sized density groups overall, but their contents are not balanced.

#### TRAIN density by class

| Density group | Generated | Real | Total |
|---|---:|---:|---:|
| LOW | 262 | 298 | 560 |
| MEDIUM | 367 | 193 | 560 |
| HIGH | 211 | 349 | 560 |

The category composition is also strongly unequal. For example:

- LOW contains 243 UI Screenshots but only 3 Tables and 5 Academic Posters;
- HIGH contains 221 Tables and 162 Academic Posters but only 7 UI Screenshots;
- within validation, some category-density cells contain only one to three images.

**Impact:** Apparent performance changes across density may actually be changes in class prior or category mix. Some per-category density comparisons are too small to interpret.

**Required correction:** Treat density primarily as a continuous variable and report category-adjusted analyses. If bins are retained for presentation, always show class/category counts and avoid conclusions from sparse cells. Consider category-specific quantiles only as a separately defined sensitivity analysis, not a silent replacement of the frozen global thresholds.

### 4. High severity: the proposed experiment order does not match the immediate feasibility goal

The existing protocol emphasizes Model A versus Model C and provisionally starts with a visual baseline. The user's immediate question is whether a text-layout pattern exists at all.

**Impact:** Fusion performance could obscure whether layout alone contains stable signal, and a complex experiment may proceed before the premise is validated.

**Required correction:** Begin with layout-only descriptive analysis and simple classifiers. Run visual/fusion experiments only after understanding what the layout branch learned.

### 5. Medium-high severity: B1 loses orientation information

The OCR JSON files preserve four-point polygons. However, `box_quantities()` in `src/layout/layout_features.py` converts each polygon into an axis-aligned envelope for B1 width, height, area, aspect ratio, and centroid calculations.

**Impact:** Slant and rotation can inflate B1 width/height/area and are not represented explicitly. This conflicts with the concern that a slanted text region should retain its slanted geometry.

B2 rasterizes the original polygon and therefore retains approximate orientation and shape, subject to 64×64 resolution.

**Required correction:** Preserve LAYOUT_FEATURES_V1 unchanged, but do not claim that B1 captures orientation. If orientation is theoretically important, define a separate versioned sensitivity representation with rotated-rectangle angle and true polygon geometry.

### 6. Medium-high severity: dataset source is confounded with authenticity

Within each category, Real images come from one named public dataset while Generated images come from the GPT-Image-2 generation pipeline.

**Impact:** A detected pattern may reflect conventions of PosterSum, Crello, ChartGalaxy, SROIE, PubTables-1M, or Enrico compared with the generation prompts. It cannot establish a universal Real-versus-AI layout rule.

**Required correction:** Frame findings as TextRich/GPT-Image-2 benchmark evidence. Analyze every category separately and avoid universal claims. External-source or cross-generator validation would be needed for generalization claims.

### 7. Medium severity: one detector cannot establish detector-independent layout signal

The frozen OCR detector is PP-OCRv6_small_det. Reproducibility within one detector is strong, but robustness to the detector choice is unverified.

**Impact:** A result may depend on PP-OCRv6 segmentation conventions.

**Required correction:** If resources allow, run a second detector only on a balanced TRAIN/validation audit subset. Compare polygon-quality ratings and conclusions from coarse layout statistics. Do not process TEST or replace the frozen primary detector during this sensitivity check.

### 8. Medium severity: B2 may lose fine geometry

B2 fills polygons on a 256×256 canvas and max-pools them to 64×64. Dense neighboring lines may merge, and thin or small regions may expand by max pooling.

**Impact:** A negative B2 result would not prove that no spatial pattern exists; it may show that the chosen rasterization did not preserve it.

**Required correction:** Interpret negative findings narrowly. A 128×128 or alternate rasterization may be considered later as a separately versioned sensitivity test only if the initial result is ambiguous.

### 9. Low severity: repository history was not independently verified in this audit

The files and artifacts were readable, but `git status` and `git log` were blocked by Git's safe-directory ownership protection in the sandbox. No global Git configuration was changed.

**Impact:** Current artifact contents were inspected, but commit history and uncommitted-state claims remain unverified in this audit.

## Calculation spot-checks

| Check | Result |
|---|---|
| Dataset manifest rows | Verified: 12,095 |
| Manifest paths present | Verified: 0 missing |
| Pilot split totals | Verified: 2,400 / 1,680 / 360 / 360 |
| Class-category balance | Verified: 140/30 per class-category cell in TRAIN/validation |
| OCR inventory rows | Verified: 2,040 |
| B1 rows | Verified: 1,680 TRAIN; 360 validation |
| B2 manifest rows | Verified: 1,680 TRAIN; 360 validation |
| B1 feature count | Verified: 16 whitelisted features |
| Density-class balance | Discrepancy from implicit balance assumption: materially imbalanced |
| Density-category balance | Discrepancy from interpretability assumption: strongly imbalanced and sparse in several cells |
| OCR box accuracy against human annotations | Not verified |
| Detector-independence | Not verified |
| Existence of stable layout signal | Not tested yet |

## Revised pilot sequence

### Phase 0 — OCR evidence quality

1. Select a balanced, TRAIN-only manual-audit subset across six categories and two classes.
2. Review overlays without filenames or displayed class labels.
3. Record missed text, false detections, poor-fit polygons, incorrect grouping/splitting, and rotation problems using a fixed rubric.
4. Compare OCR-quality measures by class and category.
5. If quality differs materially by class, treat OCR behavior as a possible explanation in every later result.

### Phase 1 — Establish what kind of layout signal exists

Use TRAIN for development and validation for confirmation. Keep TEST unopened.

1. Descriptive distributions by class and category.
2. Quantity-only baseline: count + coverage.
3. Arrangement-only baseline: position and spacing features without count/coverage.
4. Complete B1 baseline.
5. B2 map baseline.
6. Compare results overall and within categories.
7. Use permutation-label checks and resampling/confidence intervals to determine whether results are stable.

The first goal is interpretation, not maximum accuracy.

### Phase 2 — Robustness checks

1. Determine whether conclusions remain after controlling for category and continuous density.
2. Compare primary OCR with a second detector on an audit subset if feasible.
3. If orientation matters, test a separately versioned rotation-aware representation.

### Phase 3 — Complementarity

Only after Phases 0–2, compare:

- visual-only Model A;
- layout-only Models B1/B2;
- visual-layout Model C.

The main complementarity claim should be based on paired validation/test predictions and uncertainty around the difference, not on one accuracy number.

## Decision interpretation

### GO

Layout signal is stable across resampling, remains meaningful after separating quantity from arrangement, is not explained entirely by OCR-quality differences, and appears in more than one category.

### MODIFY

Signal exists but is quantity-only, category-specific, density-specific, detector-specific, or sensitive to representation choices. Narrow the thesis claim or redesign the representation.

### DROP OR PIVOT

No reproducible signal appears beyond simple quantity/OCR effects, or results collapse under category-aware and robustness checks.

## Required caveat

Even a successful pilot can support only a benchmark-scoped statement unless additional real sources and AI generators are evaluated. A negative result supports only the conclusion that the selected OCR detector and layout representations did not reveal useful signal in the tested setting.

