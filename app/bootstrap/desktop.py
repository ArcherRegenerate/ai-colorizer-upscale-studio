"""Desktop GUI entry point. Boots Qt, wires the main window to services."""
from __future__ import annotations

import sys

from loguru import logger
from PySide6.QtWidgets import QApplication

from app.config.settings import Settings
from app.handlers.main_window import MainWindow
from app.utils.logging import configure_logging


def main() -> int:
    settings = Settings.load()
    configure_logging(settings.log_level)
    logger.info("booting ai-colorizer-upscale-studio {} on {}", settings.version, settings.platform)

    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("AI Colorizer & Upscale Studio")
    window = MainWindow(settings)
    window.resize(1280, 800)
    window.show()
    return qt_app.exec()


if __name__ == "__main__":
    sys.exit(main())