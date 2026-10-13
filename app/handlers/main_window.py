"""Qt main window. Handlers here only marshal UI events into service calls."""
from __future__ import annotations

from pathlib import Path

from loguru import logger
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config.settings import Settings
from app.services.colorize_service import ColorizeService
from app.services.upscale_service import UpscaleService


class MainWindow(QMainWindow):
    """Minimal shell. Every action delegates to a service immediately."""

    def __init__(self, settings: Settings) -> None:
        super().__init__()
        self._settings = settings
        self._colorize = ColorizeService(settings)
        self._upscale = UpscaleService(settings)
        self.setWindowTitle("AI Colorizer & Upscale Studio")

        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(QLabel("Source image: (none)"))

        row = QHBoxLayout()
        self._model_box = QComboBox()
        self._model_box.addItems(["siggraph17-color", "realesrgan-x4plus"])
        row.addWidget(self._model_box)

        pick = QPushButton("Pick image…")
        pick.clicked.connect(self._on_pick)
        row.addWidget(pick)
        layout.addLayout(row)

        run = QPushButton("Run")
        run.clicked.connect(self._on_run)
        layout.addWidget(run)

        self.setCentralWidget(root)
        self._source: Path | None = None

    def _on_pick(self) -> None:
        chosen, _ = QFileDialog.getOpenFileName(self, "Open image", "", "Images (*.png *.jpg *.jpeg *.bmp *.tif)")
        if chosen:
            self._source = Path(chosen)

    def _on_run(self) -> None:
        if self._source is None:
            logger.warning("run requested with no source")
            return
        model = self._model_box.currentText()
        out = self._settings.output_dir / f"{self._source.stem}-enhanced.png"
        if "color" in model:
            self._colorize.colorize_file(self._source, out, model_name=model)
        else:
            self._upscale.upscale_file(self._source, out, scale=4, model_name=model)
        logger.info("done -> {p}", p=out)