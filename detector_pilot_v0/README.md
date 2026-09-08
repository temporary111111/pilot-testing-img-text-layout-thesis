# Fresh Detector Pilot v0

This is the planned 120-image detector QA set: 10 images per category ×
authenticity-label cell, sampled directly from the raw TextRich manifest.

The manifest is complete and deterministic. The first PP-OCRv5 CPU run was
intentionally stopped after 10 images because the server model was too slow
for an efficient full pass. Those partial outputs are retained for provenance
but are **INCOMPLETE** and must not be analyzed as a 120-image result.

The completed 24-image two-detector cross-check is in the sibling folder
`detector_crosscheck_v0/`. After manual review of that cross-check, the chosen
detector can be run on this complete 120-image QA set.

