"""Static registry of supported colorizer / upscaler model descriptors."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelDescriptor:
    name: str
    purpose: str  # "colorize" | "upscale"
    filename: str
    scale: int
    sha256: str
    min_vram_mb: int


REGISTRY: dict[str, ModelDescriptor] = {
    "siggraph17-color": ModelDescriptor(
        name="siggraph17-color",
        purpose="colorize",
        filename="siggraph17-colorization.onnx",
        scale=1,
        sha256="a1b2c3d4e5f6" + "0" * 52,
        min_vram_mb=1024,
    ),
    "eccv16-color": ModelDescriptor(
        name="eccv16-color",
        purpose="colorize",
        filename="eccv16-colorization.onnx",
        scale=1,
        sha256="9f8e7d6c5b4a" + "0" * 52,
        min_vram_mb=768,
    ),
    "realesrgan-x2plus": ModelDescriptor(
        name="realesrgan-x2plus",
        purpose="upscale",
        filename="realesrgan-x2plus.onnx",
        scale=2,
        sha256="112233445566" + "0" * 52,
        min_vram_mb=1536,
    ),
    "realesrgan-x4plus": ModelDescriptor(
        name="realesrgan-x4plus",
        purpose="upscale",
        filename="realesrgan-x4plus.onnx",
        scale=4,
        sha256="665544332211" + "0" * 52,
        min_vram_mb=2560,
    ),
}