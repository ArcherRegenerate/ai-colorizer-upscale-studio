"""CLI entry point. Thin — parses args, delegates to services."""
from __future__ import annotations

import sys
from pathlib import Path

import typer
from loguru import logger

from app.config.settings import Settings
from app.services.colorize_service import ColorizeService
from app.services.upscale_service import UpscaleService
from app.services.batch_service import BatchService
from app.utils.logging import configure_logging

app = typer.Typer(add_completion=False, help="AI colorizer / upscaler CLI.")


@app.command("colorize")
def colorize_cmd(
    src: Path = typer.Argument(..., exists=True, dir_okay=False),
    out: Path = typer.Option(Path("output/colorized.png"), "--out", "-o"),
    model: str = typer.Option("siggraph17-color", "--model"),
) -> None:
    """Colorize a single grayscale image."""
    settings = Settings.load()
    configure_logging(settings.log_level)
    svc = ColorizeService(settings)
    result = svc.colorize_file(src, out, model_name=model)
    logger.info("wrote {path} in {ms}ms", path=result.output_path, ms=result.elapsed_ms)


@app.command("upscale")
def upscale_cmd(
    src: Path = typer.Argument(..., exists=True, dir_okay=False),
    out: Path = typer.Option(Path("output/upscaled.png"), "--out", "-o"),
    scale: int = typer.Option(4, "--scale", "-s", min=2, max=8),
    model: str = typer.Option("realesrgan-x4plus", "--model"),
) -> None:
    """Upscale an image by an integer factor."""
    settings = Settings.load()
    configure_logging(settings.log_level)
    svc = UpscaleService(settings)
    result = svc.upscale_file(src, out, scale=scale, model_name=model)
    logger.info("wrote {path} in {ms}ms", path=result.output_path, ms=result.elapsed_ms)


@app.command("batch")
def batch_cmd(
    src_dir: Path = typer.Argument(..., exists=True, file_okay=False),
    out_dir: Path = typer.Option(Path("output/batch"), "--out", "-o"),
    colorize: bool = typer.Option(False, "--colorize"),
    scale: int = typer.Option(2, "--scale", "-s", min=2, max=8),
    workers: int = typer.Option(4, "--workers", "-w", min=1, max=16),
) -> None:
    """Batch-process a directory: optional colorize, then upscale."""
    settings = Settings.load()
    configure_logging(settings.log_level)
    svc = BatchService(settings)
    report = svc.run(src_dir, out_dir, colorize=colorize, scale=scale, workers=workers)
    logger.info("batch done: {ok} ok, {fail} failed", ok=report.succeeded, fail=report.failed)


def main() -> None:
    try:
        app()
    except KeyboardInterrupt:
        logger.warning("interrupted")
        sys.exit(130)


if __name__ == "__main__":
    main()