# UI screenshot manual audit v0

Review all 100 OCR overlay images in `overlays/` before opening `answer_key.csv`. The red quadrilaterals are PP-OCRv5 detector output. Keep the labels hidden while reviewing.

Use 1–5 for each CSV column:

- `box_fit_rating_1_to_5`: 1 = most boxes do not fit visible text; 5 = boxes closely fit the text.
- `missed_text_rating_1_to_5`: 1 = substantial visible text is missed; 5 = almost all visible text has a box.
- `false_nontext_box_rating_1_to_5`: 1 = many boxes are icons, logos, status symbols or decoration; 5 = almost no obvious false boxes.
- `fragmentation_rating_1_to_5`: 1 = text is frequently split into unusable pieces; 5 = segmentation is usable and consistent.
- `rotation_fit_rating_1_to_5`: 1 = rotated boxes are badly oriented; 3 = no meaningful rotated text or mixed; 5 = rotated boxes follow the text.
- `repeated_alignment_rating_1_to_5`: 1 = repeated UI rows/cards have poor or unusable box alignment; 5 = repeated text elements are consistently localized.

For rotation, use 3 and write `N/A: no rotated text` when appropriate. Note examples of status-bar symbols, icons, chart marks, or decorative text treated as text. This screening is category-level detector QA. It is not exact ground-truth localization.

After screening, select 20–30 representative or difficult images for manually drawn quadrilateral ground truth. Use those to calculate precision, recall, IoU and angle error.
