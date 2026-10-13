"""Batch orchestration over a directory of images."""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from loguru import logger

from app.config.settings import Settings
from app.models.job import BatchReport
from app.services.colorize_service import ColorizeService
from app.services.upscale_service import UpscaleService

SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


class BatchService:
    """Walks a directory, applies colorize and/or upscale to each image.

    Inputs: source dir, output dir, flags.
    Outputs: BatchReport.
    Side effects: creates output dir, writes images, logs failures.
    Error modes: per-file errors are captured into the report; a fatal
    error (e.g. output dir not writable) raises.
    Concurrency: ThreadPoolExecutor; each worker gets its own service
    instances because ORT sessions are not thread-safe.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def run(
        self,
        source_dir: Path,
        output_dir: Path,
        *,
        colorize: bool,
        scale: int,
        workers: int,
    ) -> BatchReport:
        output_dir.mkdir(parents=True, exist_ok=True)
        images = [p for p in source_dir.rglob("*") if p.suffix.lower() in SUPPORTED_SUFFIXES]
        logger.info("batch: {} images, {} workers", len(images), workers)

        report = BatchReport(total=len(images), succeeded=0, failed=0)
        t0 = time.perf_counter()

        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(self._process_one, img, output_dir, colorize, scale): img
                for img in images
            }
            for fut in as_completed(futures):
                img = futures[fut]
                try:
                    fut.result()
                    report.succeeded += 1
                except Exception as exc:  # noqa: BLE001 — captured into report
                    logger.warning("failed {}: {}", img, exc)
                    report.failed += 1
                    report.failures.append((img, str(exc)))

        report.elapsed_ms = (time.perf_counter() - t0) * 1000.0
        return report

    def _process_one(self, img: Path, output_dir: Path, colorize: bool, scale: int) -> None:
        stem = img.stem
        if colorize:
            out = output_dir / f"{stem}-colorized.png"
            ColorizeService(self._settings).colorize_file(img, out, model_name="siggraph17-color")
            img = out
        out = output_dir / f"{stem}-x{scale}.png"
        UpscaleService(self._settings).upscale_file(
            img, out, scale=scale, model_name=f"realesrgan-x{scale}plus"
        )