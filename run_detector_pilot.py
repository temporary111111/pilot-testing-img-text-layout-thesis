"""Run a fresh two-detector text-localization pilot.

This script reads only the fresh detector_pilot_v0 manifest and raw images.
It does not read the previous OCR JSONs, layout CSVs, or frozen split files.
Recognition is disabled; only polygons and detection scores are saved.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


DEFAULT_MODELS = ("PP-OCRv5_server_det", "PP-OCRv6_small_det")


def load_clean_rgb(path: Path) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGBA")
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        return Image.alpha_composite(background, image).convert("RGB")


def polygons_and_scores(result: dict) -> tuple[list[list[list[float]]], list[float]]:
    polygons = result.get("dt_polys")
    scores = result.get("dt_scores")
    if polygons is None or scores is None:
        raise KeyError(f"Detector result keys were {sorted(result.keys())}")
    polys = np.asarray(polygons)
    vals = np.asarray(scores)
    out_polys = []
    out_scores = []
    for poly, score in zip(polys, vals):
        points = np.asarray(poly).reshape(-1, 2)
        if points.shape[0] != 4:
            raise ValueError(f"Expected quadrilateral, got {points.shape[0]} points")
        out_polys.append([[float(x), float(y)] for x, y in points])
        out_scores.append(float(score))
    return out_polys, out_scores


def draw_overlay(image: Image.Image, polygons: list[list[list[float]]], path: Path) -> None:
    overlay = image.copy()
    draw = ImageDraw.Draw(overlay)
    for poly in polygons:
        points = [(round(x), round(y)) for x, y in poly]
        draw.line(points + [points[0]], fill=(255, 0, 0), width=max(2, round(min(image.size) / 500)))
    path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(path, format="PNG")


def model_fingerprint(model_name: str) -> dict:
    root = Path.home() / ".paddlex" / "official_models" / model_name
    result = {"model_name": model_name, "model_dir": str(root), "files": {}}
    for name in ("inference.json", "inference.pdiparams", "inference.yml", "config.json"):
        path = root / name
        if path.is_file():
            result["files"][name] = {
                "size": path.stat().st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS), choices=DEFAULT_MODELS)
    parser.add_argument("--device", default="cpu", help="Paddle device, e.g. cpu or gpu:0")
    args = parser.parse_args()

    from paddleocr import TextDetection

    dataset_root = args.dataset_root.resolve()
    output_dir = args.output_dir.resolve()
    rows = list(csv.DictReader(args.manifest.open("r", encoding="utf-8-sig", newline="")))
    output_dir.mkdir(parents=True, exist_ok=True)

    run_meta = {
        "script": "run_detector_pilot.py",
        "manifest": str(args.manifest.resolve()),
        "dataset_root": str(dataset_root),
        "models": list(args.models),
        "engine": "paddle_static",
        "device": args.device,
        "enable_mkldnn": False,
        "recognition": False,
        "python": platform.python_version(),
        "started_unix": time.time(),
        "model_fingerprints": [model_fingerprint(name) for name in args.models],
    }
    (output_dir / "run_metadata.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")

    for model_name in args.models:
        detector = TextDetection(
            model_name=model_name,
            engine="paddle_static",
            device=args.device,
            enable_mkldnn=False,
        )
        inventory = []
        try:
            for index, row in enumerate(rows, start=1):
                image_path = dataset_root / Path(row["relative_path"])
                record = {
                    "pilot_id": row["pilot_id"],
                    "relative_path": row["relative_path"],
                    "status": "ok",
                    "error": None,
                }
                try:
                    image = load_clean_rgb(image_path)
                    rgb = np.asarray(image, dtype=np.uint8)
                    bgr = rgb[:, :, ::-1].copy()
                    start = time.perf_counter()
                    results = detector.predict(bgr)
                    runtime = time.perf_counter() - start
                    if len(results) != 1:
                        raise RuntimeError(f"expected one result, got {len(results)}")
                    polygons, scores = polygons_and_scores(results[0])
                    record.update(
                        {
                            "image_width": image.width,
                            "image_height": image.height,
                            "num_regions": len(polygons),
                            "runtime_seconds": runtime,
                            "polygons": polygons,
                            "scores": scores,
                        }
                    )
                    draw_overlay(
                        image,
                        polygons,
                        output_dir / "overlays" / model_name / f"{row['pilot_id']}.png",
                    )
                except Exception as exc:  # keep a per-image audit record
                    record.update({"status": "error", "error": repr(exc)})
                (output_dir / "json" / model_name).mkdir(parents=True, exist_ok=True)
                (output_dir / "json" / model_name / f"{row['pilot_id']}.json").write_text(
                    json.dumps(record, indent=2), encoding="utf-8"
                )
                inventory.append(
                    {
                        key: value
                        for key, value in record.items()
                        if key not in {"polygons", "scores"}
                    }
                )
                print(f"{model_name} {index}/{len(rows)} {row['pilot_id']} {record['status']}", flush=True)
        finally:
            try:
                detector.close()
            except Exception:
                pass
        with (output_dir / f"inventory_{model_name}.csv").open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=inventory[0].keys())
            writer.writeheader()
            writer.writerows(inventory)

    run_meta["finished_unix"] = time.time()
    (output_dir / "run_metadata.json").write_text(json.dumps(run_meta, indent=2), encoding="utf-8")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
