# Fresh Detector Cross-check v0

This folder is independent of the previous OCR/layout artifacts. It was built
from the raw TextRich `dataset.csv` and contains 24 images: two images per
category × authenticity-label cell.

## Detectors

- `PP-OCRv5_server_det`
- `PP-OCRv6_small_det`

Both runs used text detection only, CPU, `paddle_static`, and
`enable_mkldnn=False`. Recognized words were not stored.

## Completed results

- 24/24 images completed successfully for each detector.
- PP-OCRv5: 1,628 regions total; mean 67.83 per image.
- PP-OCRv6: 1,550 regions total; mean 64.58 per image.
- Mean greedy polygon matches at IoU ≥ 0.50: 59.67 per image.
- Mean matched fraction relative to the larger detector count: approximately
  83% (agreement is a robustness signal, not ground-truth accuracy).
- Mean normalized polygon-union coverage was similar: 0.2195 for PP-OCRv5
  and 0.2212 for PP-OCRv6.
- Absolute coverage difference was ≤ 0.05 on 23/24 images.

## Interpretation status

These results do not yet choose a winner. The detectors often agree on the
occupied page regions but differ in granularity: one may split a line into
words while the other groups it into a line. Some UI icons and decorative
elements are also detected as text-like regions. Manual review is required
before selecting a representation or using region count as a feature.

Open the paired overlays under:

```text
overlays/PP-OCRv5_server_det/
overlays/PP-OCRv6_small_det/
```

Use `detector_pilot_blind_review.csv` to map anonymous IDs to raw image paths.
The full comparison is in `detector_comparison.json`.

