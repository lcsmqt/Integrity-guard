from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from src.models import Config

DEFAULT_INCLUDE = ["**/*"]
DEFAULT_EXCLUDE = [
    "**/.git/**",
    "**/__pycache__/**",
    "**/*.pyc",
    "**/.venv/**",
    "**/node_modules/**",
]
DEFAULT_DB_PATH = "data/integrity.db"
DEFAULT_REPORT_DIR = "reports"
DEFAULT_LOG_LEVEL = "INFO"


def load_config(config_path: str | Path) -> Config:
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError("A configuração YAML deve ser um mapeamento.")

    paths = _as_str_list(raw.get("paths"), field_name="paths")
    if not paths:
        raise ValueError("A configuração precisa de pelo menos um caminho em 'paths'.")

    include = _as_str_list(raw.get("include"), field_name="include") or list(DEFAULT_INCLUDE)
    exclude = _as_str_list(raw.get("exclude"), field_name="exclude") or list(DEFAULT_EXCLUDE)

    return Config(
        paths=paths,
        include=include,
        exclude=exclude,
        db_path=str(raw.get("db_path") or DEFAULT_DB_PATH),
        report_dir=str(raw.get("report_dir") or DEFAULT_REPORT_DIR),
        log_level=str(raw.get("log_level") or DEFAULT_LOG_LEVEL),
        follow_symlinks=bool(raw.get("follow_symlinks", False)),
    )


def dump_example_config() -> Dict[str, Any]:
    return {
        "paths": ["./samples"],
        "include": list(DEFAULT_INCLUDE),
        "exclude": list(DEFAULT_EXCLUDE),
        "db_path": DEFAULT_DB_PATH,
        "report_dir": DEFAULT_REPORT_DIR,
        "log_level": DEFAULT_LOG_LEVEL,
        "follow_symlinks": False,
    }


def _as_str_list(value: Any, field_name: str) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return list(value)
    raise ValueError(f"O campo '{field_name}' deve ser uma lista de strings.")
