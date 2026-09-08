# AI Handoff: Thesis Proposal Context

> Read `CONTINUE_HERE.md` first. It records the latest category-focused direction,
> artifact map, and corrections to overstrong interpretations below. Historical
> quantity-only scores include confidence; count matching is not full density
> control; universal cross-category transfer is not a thesis success requirement.

## Purpose of this file

This file preserves the working context of the thesis discussion so it can be given to another AI assistant or used in a future chat. Read this file together with the original proposal before continuing the work.

## Student and project context

The user is a Computer Science student preparing a thesis proposal. The current proposal file is:

`Non-Semantic OCR-Derived Spatial Layout Cues for AI-Generated Text-Rich Image Detection Across Multiple Architectures and Text-Density Levels (1).md`

The proposal title inside the document is:

**OCR-Derived Spatial Layout Cues for AI-Generated Text-Rich Image Detection Across Multiple Architectures and Text-Density Levels**

The filename uses “Non-Semantic,” which refers to the intentional exclusion of recognized words and word meaning from the OCR-derived input.

## Core research idea

The study asks whether the spatial arrangement of text regions detected by OCR can provide useful information for distinguishing real text-rich images from AI-generated text-rich images.

The study is not intended to understand the text. OCR should be used only to locate text regions and describe their geometry. Recognized words, spelling, grammar, meaning, and other semantic text information should not be used as classifier inputs.

The proposed comparison has three configurations:

1. **Visual-only:** uses image pixels or learned visual features.
2. **Layout-only:** uses OCR-derived spatial information.
3. **Visual-layout fusion:** combines visual features with OCR-derived spatial information.

The study plans to evaluate these configurations across multiple selected architectures and across low, medium, and high text-density levels. Text density is intended for analysis and grouping, not as a direct model input.

## Proposed dataset and evaluation

The proposal uses the TextRich benchmark, with six text-rich image categories:

- academic posters
- commercial posters
- infographic charts
- receipts
- tables
- user-interface screenshots

The task is binary classification: real versus AI-generated images.

Planned metrics include accuracy, precision, recall, F1-score, macro-F1, and ROC-AUC. Results should be examined overall, by image category, and by text-density level.

The proposal does not assume that the combined model must perform better. Positive, mixed, or negative results are all valid findings.

## Current concern: pilot testing is required first

The group is not yet certain that the thesis premise is strong enough. Before committing to the full study, they want a pilot test to determine:

1. whether there is a stable layout pattern separating real and AI-generated images; and
2. whether the OCR detector can produce sufficiently accurate and consistent text-region geometry.

The main risk is a confound: the classifier might learn OCR errors, missed detections, or different OCR behavior between real and AI images instead of learning genuine spatial-layout cues.

Therefore, the pilot should evaluate OCR geometry and robustness before training a complex final classifier.

## Important geometry requirement

The group specifically raised the case of slanted or rotated text. A simple horizontal/vertical bounding rectangle may include excessive whitespace and lose the actual text orientation. For this study, the preferred representation is:

- a four-point polygon/quadrilateral, or
- a rotated bounding box with an orientation angle.

The pipeline should preserve the original polygon coordinates rather than immediately converting every region to `xmin, ymin, xmax, ymax`.

The project must also define the text-region unit consistently: word-level, line-level, or block-level. Line-level or block-level regions may be more stable for page-level layout analysis, but the choice must be fixed across all images.

## Current OCR recommendation

The current practical recommendation is:

**Primary detector:** PaddleOCR PP-OCRv5 server text detector, using the text-detection module only and preserving quadrilateral polygon outputs and detection confidence.

Recognition is not required for the layout input. The detector should provide geometry; recognized text and word meaning should be discarded from the classifier pipeline.

PaddleOCR was recommended because its documented outputs and settings support quadrilateral detection boxes, it has a separate text-detection module, and it is practical for mixed text-rich images. For a lightweight prototype, a mobile detector variant can be considered after the accuracy pilot.

**Robustness check:** run a second detector, such as MMOCR DBNet/DBNet++ or docTR, on a smaller common subset. If both detectors produce similar spatial statistics and the same general findings, the result is less likely to be an artifact of one OCR system.

Tesseract was not recommended as the primary detector because its typical bounding-box behavior is less suitable for rotated/slanted text and dense generated layouts.

## Existing implementation state discovered after dataset download

The downloaded dataset is located at:

`C:\Users\dev\desktop\text-rich-ai-image-detector\data\TextRich\`

That directory contains `dataset.csv`, the `Data/` image hierarchy, and the dataset README. The manifest has **12,095 images**: **5,986 real** and **6,109 AI-generated**, across the six expected categories. A read-only path check found **zero missing files** for the manifest entries.

There is also an existing implementation workspace at:

`C:\Users\dev\desktop\text-rich-ai-image-detector\`

It already contains project documentation, a `.venv-ocr` environment, OCR scripts, frozen split files, reports, and layout artifacts. Its current source-of-truth documents state that the following work is complete:

- frozen 2,400-image pilot: 1,680 train, 360 validation, 360 test;
- PP-OCRv6_small_det text detection only, with no recognition text stored;
- TRAIN+VAL OCR extraction: 2,040/2,040 successful, 145,771 valid polygons, zero errors and zero zero-detection images;
- frozen `LAYOUT_FEATURES_V1` representation;
- B1: exactly 16 geometric layout features;
- B2: 64×64 binary polygon-layout maps;
- text-density thresholds derived from TRAIN only and frozen in `reports/T006_density_thresholds.json`.

This existing project state supersedes the earlier provisional PP-OCRv5 recommendation for the current pilot. Do not switch the detector or regenerate frozen artifacts without an explicit research decision. The current project documentation also says that classifier training and TEST OCR processing require a separate approved task packet; do not start those automatically.

The existing OCR audit confirms technical validity of the polygons (four vertices, finite coordinates, in bounds), but this does **not** prove that the polygons are semantically perfect human ground truth. Visual overlay review and/or a manual annotation check may still be useful if the research question requires box-level accuracy evidence.

A read-only visual inspection of five available T004 overlays (academic poster, table, receipt, commercial poster, and UI screenshot) found no obvious gross box failures in those samples. Text-line regions were generally tightly outlined, and one rotated UI word was represented with a visibly rotated quadrilateral. This is only an informal 5-image check; it is not a formal OCR accuracy measurement and should not be reported as one.

## Audit finding about the frozen layout features

The existing implementation has an important distinction:

- **B2** rasterizes the original quadrilateral polygons into a 64×64 binary map, so it retains approximate polygon shape and position.
- **B1** computes several size/shape statistics from an **axis-aligned bounding box** around each polygon (`box_quantities()`), including width, height, area, and aspect ratio. These B1 features can lose or distort rotation information for slanted text even when the OCR polygon itself is accurate.

This is not automatically an error because the current study is about page-level layout and B1/B2 were frozen as `LAYOUT_FEATURES_V1`. However, it is a methodological limitation relevant to the original concern about slanted text. Do not silently add rotation-aware B1 features or regenerate frozen artifacts. If orientation becomes a required research variable, create a separately versioned representation and obtain an explicit research decision.

## Suggested OCR output schema

For every detected region, save at least:

```text
image_id
polygon_points = [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
normalized_polygon_points
detection_confidence
area
orientation_angle
```

Do not use recognition text, recognized words, or semantic content in the layout classifier.

## Suggested pilot workflow

1. Select a small but balanced subset covering all image categories, both real and AI-generated classes, and all intended text-density levels.
2. Run the primary OCR detector using fixed settings and save polygons, confidence values, and visual overlays.
3. Manually annotate a representative subset of text regions.
4. Measure detection recall, precision, polygon overlap/IoU, and angle error where applicable.
5. Check whether OCR failures or box counts differ systematically between real and AI images.
6. Create simple layout features and/or normalized occupancy maps from polygons.
7. Test simple group differences or a shallow baseline classifier before using deep architectures.
8. Repeat the analysis with a second detector and with small box perturbations or threshold changes.
9. Decide whether the layout signal is stable enough to justify the full thesis.

## Candidate layout representations

Possible non-semantic features include:

- text-region count
- total text-area coverage
- region area distribution
- centroids and normalized positions
- row/column alignment
- spacing and gap statistics
- overlap and relative arrangement
- orientation-angle distribution
- normalized binary occupancy or layout map

OCR confidence, number of missed boxes, and recognition quality should initially be treated as quality-control variables rather than layout features. Otherwise, the model may learn OCR behavior instead of layout.

## Possible pilot decision rules

- If OCR geometry is unreliable, improve or replace the detector before studying classification.
- If OCR is reliable but no stable layout signal exists, reconsider or narrow the thesis.
- If a signal exists only in one category or density level, narrow the claim accordingly.
- If the signal remains under detector changes and small geometric perturbations, proceed to the larger controlled experiment.

## Open decisions for the next discussion

These items are not finalized yet:

- exact OCR version and checkpoint;
- whether the main representation is quadrilateral polygons, rotated rectangles, masks, or a combination;
- word-level versus line-level versus block-level regions;
- exact text-density formula and low/medium/high thresholds;
- exact selected visual architectures;
- size and sampling strategy of the manually annotated pilot subset;
- acceptance criteria for OCR quality and layout-signal robustness;
- dataset split and prevention of leakage between related images.

## Guidance for the next AI assistant

Do not assume that the thesis premise is already validated. Help the group design and interpret the pilot first. Keep the distinction clear between:

1. true spatial-layout information,
2. OCR detector quality or failure patterns, and
3. semantic text information, which is intentionally excluded.

When recommending tools or models, prioritize polygon/rotated-box geometry, reproducibility, fixed settings, visual inspection, and measurable validation. Do not claim that the combined visual-layout model must outperform the visual-only model.

## Independent audit added

An independent methodology audit was created at:

`C:\Users\dev\desktop\feasibility-testing-thesis\PREVIOUS_WORK_METHODOLOGY_AUDIT.md`

Its main conclusion is that the existing engineering foundation can be preserved, but the layout hypothesis is **not yet validated**. The highest-priority risks are OCR accuracy versus mere technical success, confounding of spatial arrangement with text quantity and OCR segmentation, strongly imbalanced global density groups by category/class, and loss of rotation information in B1 axis-aligned features. The recommended sequence is OCR-quality audit → quantity/arrangement ablations → category/density robustness checks → visual/fusion experiments.
## Fresh detector pilot started

To avoid relying on the previous derived artifacts, a new independent manifest was created directly from raw TextRich data:

- `C:\Users\dev\desktop\feasibility-testing-thesis\detector_pilot_v0\detector_pilot_manifest.csv` — 120 images, 10 per category × label cell;
- `C:\Users\dev\desktop\feasibility-testing-thesis\detector_pilot_v0\detector_pilot_blind_review.csv` — same images without labels for manual review;
- `C:\Users\dev\desktop\feasibility-testing-thesis\detector_crosscheck_v0\` — completed 24-image PP-OCRv5/PP-OCRv6 cross-check.

Both detectors succeeded technically on 24/24 cross-check images. Their polygon counts differed, but normalized polygon-union coverage was close on most images. Visual inspection showed that the main difference is often segmentation granularity (word-level versus line-level), with occasional UI/decorative elements detected as text-like regions. This means occupancy-map geometry may be more stable than raw region count, but detector choice is not finalized until manual review.

## Hardware note

The host PC has an **NVIDIA GeForce RTX 3050 Laptop GPU with 4 GB VRAM** and an integrated AMD Radeon GPU. `nvidia-smi` reports an NVIDIA driver with CUDA 13.0 support. The existing `.venv-ocr` currently contains a CPU-only Paddle build (`paddle 3.3.1`, `compiled_with_cuda=False`, active device `cpu`). A separate `.venv-ocr-gpu` environment was created for the validated GPU runs described below.

## GPU validation and feature pilot update

The separate `.venv-ocr-gpu` environment uses PaddlePaddle 3.3.0 GPU. A 24-image CPU/GPU cross-check matched region counts on every image; PP-OCRv5 polygon coordinates were identical, and PP-OCRv6 differed by at most 2 pixels with negligible normalized coverage differences. The validation details are in `GPU_CPU_DETECTOR_VALIDATION.md`.

The full fresh 120-image PP-OCRv5 GPU run completed 120/120 successfully. Its outputs are in `detector_pilot_gpu_v0`. The run contains 8,617 valid polygons across 60 real and 60 generated images, balanced at 10 images per category-label cell.

The first feature pilot is in `feature_pilot_v0`. It separates quantity/density features from arrangement features and evaluates them with a 5-fold stratified nearest-centroid baseline. Pooled balanced accuracy was 0.700 for quantity-only, 0.667 for arrangement-only, and 0.708 for the combined group. These values are feasibility signals only: density overlap is limited in the 120-image sample, and within-category sample sizes are 10 per class. The next experiment should expand the sample and enforce stronger density overlap before treating arrangement as an independent signal.

The expanded feature pilot is in `feature_pilot_expanded_v0`. It uses 600 images (50 per category-label cell), 42,642 valid polygons, and no missing or infinite feature values after fixing duplicate-centroid distance handling. Full-sample pooled balanced accuracy was 0.720 quantity-only, 0.670 arrangement-only, and 0.733 combined. After greedy within-category count matching, arrangement-only fell to 0.571 for pairs with region-count difference <=10 and 0.605 for difference <=20, while quantity-only remained 0.770 and 0.744. This is evidence that the initial arrangement signal is substantially confounded by text quantity and category-specific structure. The current thesis claim should remain unvalidated; consider a category-conditional scope or a redesigned arrangement representation with stricter source controls before investing in final architectures.

An additional leave-one-category-out check was run on the expanded features. Mean balanced accuracy was 0.602 for arrangement-only, 0.678 for quantity-only, and 0.682 for the combined group. On the <=10 density-matched subset, arrangement-only was 0.461 and quantity-only 0.703; on the <=20 subset, arrangement-only was 0.488 and quantity-only 0.669. These generalization checks further weaken the claim of a universal arrangement-only signal across categories.

The current manual audit focus is `manual_audit_ui_v0`, which contains all 100 UI
original images and local PP-OCRv5 overlays, a label-blind `blind_review.csv`, an
`answer_key.csv`, and `RATING_GUIDE.md`. Review all 100 overlays before opening the
answer key. This package exists because UI is a promising category for testing text
alignment and repeated component spacing, but icons, status-bar symbols, source
templates and low-contrast text remain detector-quality risks.
