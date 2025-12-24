import logging
from pathlib import Path

from etc.settings import setup_logging

from scripts import ejemplo_compresión


setup_logging()
logger: logging.Logger = logging.getLogger(Path(__file__).parent.name)


if __name__ == "__main__":
    ejemplo_compresión.ejemplo()
