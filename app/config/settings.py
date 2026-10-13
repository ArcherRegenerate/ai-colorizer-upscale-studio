"""Immutable, environment-aware settings for the studio."""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_cache_dir, user_data_dir

from app import __version__


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings. Loaded once, passed to every service.

    Inputs: none (classmethod `.load()` reads env + platformdirs).
    Outputs: frozen Settings instance.
    Side effects: creates cache/data dirs on disk.
    Error modes: raises RuntimeError if the data dir cannot be created.
    """

    version: str
    platform: str
    log_level: str
    data_dir: Path
    cache_dir: Path
    weights_dir: Path
    output_dir: Path
    device: str
    max_workers: int

    @classmethod
    def load(cls) -> "Settings":
        data_dir = Path(os.environ.get("ACUS_DATA_DIR", user_data_dir("ai-colorizer-upscale-studio")))
        cache_dir = Path(os.environ.get("ACUS_CACHE_DIR", user_cache_dir("ai-colorizer-upscale-studio")))
        weights_dir = data_dir / "models" / "weights"
        output_dir = Path(os.environ.get("ACUS_OUTPUT_DIR", Path.cwd() / "output"))

        for d in (data_dir, cache_dir, weights_dir, output_dir):
            try:
                d.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                raise RuntimeError(f"cannot create {d}: {exc}") from exc

        return cls(
            version=__version__,
            platform=sys.platform,
            log_level=os.environ.get("ACUS_LOG_LEVEL", "INFO"),
            data_dir=data_dir,
            cache_dir=cache_dir,
            weights_dir=weights_dir,
            output_dir=output_dir,
            device=os.environ.get("ACUS_DEVICE", "auto"),
            max_workers=int(os.environ.get("ACUS_WORKERS", "4")),
        )