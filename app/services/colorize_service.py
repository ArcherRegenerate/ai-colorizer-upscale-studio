"""Colorization service — grayscale image in, colorized image out."""
from __future__ import annotations

import time
import uuid
from pathlib import Path

import numpy as np
from loguru import logger

from app.adapters.onnx_adapter import OnnxRuntimeAdapter
from app.config.model_registry import REGISTRY
from app.config.settings import Settings
from app.models.job import JobKind, JobResult
from app.utils.image_io import load_image_rgb, save_image_rgb


class ColorizeService:
    """Wraps a colorization ONNX model.

    Inputs: a source path to a grayscale (or RGB — it will be desaturated
    to L channel) image, an output path, and a model name present in the
    registry with `purpose="colorize"`.
    Outputs: JobResult with output path and wall-clock timing.
    Side effects: writes the colorized image to disk.
    Error modes: raises FileNotFoundError on missing source, KeyError on
    unknown model, RuntimeError on inference failure.
    Concurrency: the underlying ORT session is not thread-safe; one
    instance per worker thread.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._adapter = OnnxRuntimeAdapter(settings)

    def colorize_file(self, source: Path, destination: Path, *, model_name: str) -> JobResult:
        if not source.is_file():
            raise FileNotFoundError(source)
        desc = REGISTRY[model_name]
        if desc.purpose != "colorize":
            raise ValueError(f"{model_name} is not a colorizer")

        t0 = time.perf_counter()
        rgb = load_image_rgb(source)
        l_channel = self._to_lab_l(rgb)
        lab_ab = self._adapter.run_colorize(desc, l_channel)
        colorized = self._merge_lab(l_channel, lab_ab)
        save_image_rgb(colorized, destination)
        elapsed = (time.perf_counter() - t0) * 1000.0

        logger.debug("colorized {} -> {}", source.name, destination.name)
        return JobResult(
            job_id=str(uuid.uuid4()),
            kind=JobKind.COLORIZE,
            output_path=destination,
            input_size=(rgb.shape[1], rgb.shape[0]),
            output_size=(colorized.shape[1], colorized.shape[0]),
            elapsed_ms=elapsed,
            device_used=self._adapter.device,
        )

    @staticmethod
    def _to_lab_l(rgb: np.ndarray) -> np.ndarray:
        import cv2

        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
        return lab[..., 0:1].astype(np.float32) / 255.0

    @staticmethod
    def _merge_lab(l: np.ndarray, ab: np.ndarray) -> np.ndarray:
        import cv2

        lab = np.concatenate([l * 255.0, ab * 128.0], axis=-1).astype(np.uint8)
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)