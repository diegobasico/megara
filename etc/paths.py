from pathlib import Path
from dataclasses import dataclass


_BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass
class _LocalPaths:
    data: Path = _BASE_DIR / "data"
    tmp: Path = _BASE_DIR / "tmp"
    config: Path = _BASE_DIR / "etc"
    db: Path = _BASE_DIR / "data" / "db"
    logs: Path = _BASE_DIR / "tmp" / "logs"
    cache: Path = _BASE_DIR / "tmp" / "cache"
    log_config: Path = _BASE_DIR / "etc" / "log_config.yaml"


local_paths = _LocalPaths()
