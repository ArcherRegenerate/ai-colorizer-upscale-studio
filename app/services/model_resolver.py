"""Resolves model files: local cache first, then download, then error."""
from __future__ import annotations

import hashlib
from pathlib import Path

import httpx
from loguru import logger

from app.config.model_registry import REGISTRY, ModelDescriptor
from app.config.settings import Settings

CDN_BASE = "https://models.colorizer-upscale.studio/v1"


class ModelResolver:
    """Finds or fetches a model file.

    Inputs: model name in REGISTRY.
    Outputs: absolute Path to a verified .onnx file.
    Side effects: may download and write into `settings.weights_dir`.
    Error modes: RuntimeError if download fails or sha256 mismatches.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def resolve(self, model_name: str) -> Path:
        desc = REGISTRY[model_name]
        target = self._settings.weights_dir / desc.filename
        if target.is_file() and self._verify(target, desc):
            return target
        self._download(desc, target)
        if not self._verify(target, desc):
            raise RuntimeError(f"sha256 mismatch after download: {target}")
        return target

    def _download(self, desc: ModelDescriptor, target: Path) -> None:
        url = f"{CDN_BASE}/{desc.filename}"
        logger.info("downloading {} -> {}", url, target)
        tmp = target.with_suffix(".part")
        with httpx.stream("GET", url, timeout=120.0, follow_redirects=True) as r:
            r.raise_for_status()
            with tmp.open("wb") as fh:
                for chunk in r.iter_bytes(1 << 20):
                    fh.write(chunk)
        tmp.replace(target)

    @staticmethod
    def _verify(path: Path, desc: ModelDescriptor) -> bool:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest().startswith(desc.sha256)