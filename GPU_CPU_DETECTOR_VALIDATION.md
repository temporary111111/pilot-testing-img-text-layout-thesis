# CPU/GPU Detector Validation

Date: 2026-09-07

## Setup

- GPU: NVIDIA GeForce RTX 3050 Laptop GPU, 4 GB
- PaddlePaddle: 3.3.0 GPU build
- Device: `gpu:0`
- Models: `PP-OCRv5_server_det`, `PP-OCRv6_small_det`
- Images: same 24-image detector cross-check manifest used for the earlier CPU run
- Recognition: disabled; detection polygons only

## Results

| Model | CPU regions | GPU regions | Equal counts | Max polygon-coordinate difference | Mean normalized coverage difference | Mean runtime CPU | Mean runtime GPU |
|---|---:|---:|---:|---:|---:|---:|---:|
| PP-OCRv5_server_det | 1,628 | 1,628 | 24/24 | 0 px | 0.000000 | 15.93 s | 0.271 s |
| PP-OCRv6_small_det | 1,550 | 1,550 | 24/24 | 2 px | 0.000023 | 1.767 s | 0.122 s |

The PP-OCRv5 score differences were negligible (maximum approximately 0.000007). PP-OCRv6 had slightly larger score variation (maximum approximately 0.043), but region counts matched on every image and normalized coverage differences stayed below 0.001 on all 24 images.

## Interpretation

For this pilot, GPU inference is operationally consistent with the existing CPU outputs. The GPU run can be used for subsequent detector QA, while keeping the CPU/GPU validation record with the artifacts. This validates reproducibility across devices; it does not establish detector accuracy. Manual overlay review and, if possible, box-level annotation remain necessary.

Initial pilot recommendation: use `PP-OCRv5_server_det` as the primary detector because it is the larger server model and produced slightly more granular detections; retain `PP-OCRv6_small_det` as a sensitivity check rather than treating either detector as ground truth.
