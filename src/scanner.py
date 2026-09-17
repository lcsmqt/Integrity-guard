from __future__ import annotations

import logging
from fnmatch import fnmatch
from pathlib import Path
from typing import Iterable, List, Sequence

from src.hashing import get_file_info
from src.models import Config, FileInfo

logger = logging.getLogger(__name__)


def scan_paths(config: Config) -> List[FileInfo]:
    """Walk authorized local paths and return hashed file records."""
    collected: List[FileInfo] = []
    seen: set[str] = set()

    for raw_path in config.paths:
        root = Path(raw_path)
        if not root.exists():
            logger.warning("Caminho configurado não existe: %s", root)
            continue
        if root.is_file():
            candidates = [root]
        else:
            candidates = [item for item in root.rglob("*") if item.is_file()]

        for candidate in candidates:
            if not _is_included(candidate, root, config.include, config.exclude):
                continue
            if candidate.is_symlink() and not config.follow_symlinks:
                logger.debug("Ignorando symlink: %s", candidate)
                continue
            try:
                info = get_file_info(candidate)
            except OSError as exc:
                logger.warning("Não foi possível ler %s: %s", candidate, exc)
                continue
            if info.path in seen:
                continue
            seen.add(info.path)
            collected.append(info)

    collected.sort(key=lambda item: item.path)
    logger.info("Varredura concluída: %s arquivos", len(collected))
    return collected


def scan_files(paths: Sequence[str], exclude: Sequence[str], include: Sequence[str] | None = None) -> List[FileInfo]:
    config = Config(
        paths=list(paths),
        include=list(include or ["**/*"]),
        exclude=list(exclude),
        db_path="data/integrity.db",
        report_dir="reports",
        log_level="INFO",
    )
    return scan_paths(config)


def _is_included(
    path: Path,
    root: Path,
    include: Iterable[str],
    exclude: Iterable[str],
) -> bool:
    relative = _relative_posix(path, root)
    if any(_match_glob(relative, pattern) or _match_glob(path.as_posix(), pattern) for pattern in exclude):
        return False
    include_patterns = list(include) or ["**/*"]
    return any(_match_glob(relative, pattern) or _match_glob(path.as_posix(), pattern) for pattern in include_patterns)


def _relative_posix(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _match_glob(value: str, pattern: str) -> bool:
    normalized = pattern.replace("\\", "/")
    if fnmatch(value, normalized):
        return True
    if normalized.endswith("/**"):
        prefix = normalized[:-3]
        if value == prefix or value.startswith(prefix.rstrip("/") + "/"):
            return True
    return False
