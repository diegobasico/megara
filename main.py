import logging
from pathlib import Path

from etc.settings import setup_logging


setup_logging()
logger: logging.Logger = logging.getLogger(Path(__file__).parent.name)


if __name__ == "__main__":
    from scripts.ejemplo_flexión_1 import ejemplo

    ejemplo()
