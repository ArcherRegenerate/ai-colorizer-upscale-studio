"""Job and result schemas shared across services."""
from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class JobKind(str, Enum):
    COLORIZE = "colorize"
    UPSCALE = "upscale"
    BATCH = "batch"


class JobRequest(BaseModel):
    """Inbound request. Path values are validated to exist by the service."""

    kind: JobKind
    source: Path
    destination: Path
    model_name: str
    scale: int = Field(default=1, ge=1, le=8)
    tile_size: int = Field(default=512, ge=128, le=2048)
    preserve_exif: bool = True


class JobResult(BaseModel):
    """Outbound result. `elapsed_ms` is wall-clock, not GPU time."""

    job_id: str
    kind: JobKind
    output_path: Path
    input_size: tuple[int, int]
    output_size: tuple[int, int]
    elapsed_ms: float
    device_used: str


class BatchReport(BaseModel):
    total: int
    succeeded: int
    failed: int
    failures: list[tuple[Path, str]] = Field(default_factory=list)
    elapsed_ms: float = 0.0