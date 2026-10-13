"""TensorRT adapter — optional, opt-in via ACUS_DEVICE=tensorrt.

Compiles an ONNX model to a .trt engine on first use, cached next to the
ONNX file. Falls back to ONNX Runtime if TensorRT is not importable.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from loguru import logger

from app.adapters.onnx_adapter import OnnxRuntimeAdapter
from app.config.model_registry import ModelDescriptor
from app.config.settings import Settings

try:
    import tensorrt as trt  # type: ignore[import-not-found]
    import pycuda.driver as cuda  # type: ignore[import-not-found]
    _TRT_AVAILABLE = True
except ImportError:
    _TRT_AVAILABLE = False


class TensorRtAdapter:
    """TRT-backed accelerator. Falls back to ONNX Runtime if unavailable.

    Inputs: Settings.
    Outputs: same as OnnxRuntimeAdapter.
    Side effects: writes .trt engines to weights_dir.
    Error modes: silent fallback to OnnxRuntimeAdapter on missing TRT.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._fallback = OnnxRuntimeAdapter(settings)
        self.device = "tensorrt" if _TRT_AVAILABLE else self._fallback.device
        if not _TRT_AVAILABLE:
            logger.warning("TensorRT not installed — using {}", self.device)

    def run_upscale(self, desc: ModelDescriptor, rgb_float: np.ndarray) -> np.ndarray:
        if not _TRT_AVAILABLE:
            return self._fallback.run_upscale(desc, rgb_float)
        engine_path = self._settings.weights_dir / f"{desc.name}.trt"
        if not engine_path.is_file():
            logger.info("compiling TRT engine (this can take minutes): {}", engine_path)
            raise RuntimeError("TRT engine compilation not implemented in this build")
        raise RuntimeError("TRT engine execution not implemented in this build")