from pathlib import Path

from src.models import Config
from src.scanner import scan_paths


def _config(tmp_path: Path, **overrides) -> Config:
    data = {
        "paths": [str(tmp_path)],
        "include": ["**/*"],
        "exclude": ["**/*.tmp", "**/skip/**"],
        "db_path": str(tmp_path / "integrity.db"),
        "report_dir": str(tmp_path / "reports"),
        "log_level": "INFO",
        "follow_symlinks": False,
    }
    data.update(overrides)
    return Config(**data)


def test_scan_paths_respects_include_and_exclude(tmp_path: Path) -> None:
    (tmp_path / "keep.txt").write_text("keep", encoding="utf-8")
    (tmp_path / "ignore.tmp").write_text("tmp", encoding="utf-8")
    nested = tmp_path / "skip"
    nested.mkdir()
    (nested / "secret.txt").write_text("nope", encoding="utf-8")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "ok.md").write_text("ok", encoding="utf-8")

    files = scan_paths(_config(tmp_path, include=["**/*.txt", "**/*.md"]))
    names = sorted(Path(item.path).name for item in files)
    assert names == ["keep.txt", "ok.md"]
