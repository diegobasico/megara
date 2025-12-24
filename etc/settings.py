import sys
import locale
import logging
import logging.config
from pathlib import Path

import yaml

from etc.paths import local_paths


def load_logging_config(config_path: Path):
    """Load logging configuration from a YAML file."""

    config_path = Path(config_path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"Logging config file not found at: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    logging.config.dictConfig(config)


def handle_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """Handles Ctrl+C interruption."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Let CTRL+C behave normally
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.getLogger(__name__).error(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )


def setup_logging():
    """Load logging settings to the entire application."""
    locale.setlocale(locale.LC_TIME, "es_PE.utf8")
    load_logging_config(local_paths.log_config)
    sys.excepthook = handle_uncaught_exceptions
