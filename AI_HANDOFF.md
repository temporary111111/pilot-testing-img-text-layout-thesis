# AI Handoff: Thesis Proposal Context

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
