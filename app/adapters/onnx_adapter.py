"""ONNX Runtime adapter. Isolates ORT so services never touch it directly."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import onnxruntime as ort
from loguru import logger

from app.config.model_registry import ModelDescriptor
from app.config.settings import Settings
from app.services.model_resolver import ModelResolver


class OnnxRuntimeAdapter:
    """Wraps a single ORT InferenceSession per model, lazily built.

    Inputs: Settings, plus per-call ModelDescriptor + np.ndarray.
    Outputs: np.ndarray of the same spatial layout as the model expects.
    Side effects: caches sessions in memory; downloads models on demand.
    Error modes: RuntimeError if ORT providers are unavailable.
    Concurrency: sessions are cached and re-used; callers must not share
    one adapter across threads (ORT is thread-safe for Run, but session
    creation is not).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._resolver = ModelResolver(settings)
        self._sessions: dict[str, ort.InferenceSession] = {}
        self.device = self._pick_device()

    def _pick_device(self) -> str:
        if self._settings.device != "auto":
            return self._settings.device
        providers = ort.get_available_providers()
        if "CUDAExecutionProvider" in providers:
            return "cuda"
        if "DmlExecutionProvider" in providers:
            return "directml"
        return "cpu"

    def _session(self, desc: ModelDescriptor) -> ort.InferenceSession:
        if desc.name in self._sessions:
            return self._sessions[desc.name]
        path = self._resolver.resolve(desc.name)
        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if self.device == "cuda"
            else ["CPUExecutionProvider"]
        )
        sess = ort.InferenceSession(str(path), providers=providers)
        logger.info("loaded {} on {}", desc.name, providers[0])
        self._sessions[desc.name] = sess
        return sess

    def run_colorize(self, desc: ModelDescriptor, l_channel: np.ndarray) -> np.ndarray:
        sess = self._session(desc)
        name = sess.get_inputs()[0].name
        out = sess.run(None, {name: l_channel[None, ...]})[0]
        return out[0].transpose(1, 2, 0)  # CHW -> HWC

    def run_upscale(self, desc: ModelDescriptor, rgb_float: np.ndarray) -> np.ndarray:
        sess = self._session(desc)
        name = sess.get_inputs()[0].name
        chw = rgb_float.transpose(2, 0, 1)[None, ...]
        out = sess.run(None, {name: chw})[0]
        return out[0].transpose(1, 2, 0)