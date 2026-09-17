from __future__ import annotations

import hashlib
from pathlib import Path
from typing import BinaryIO

from src.models import FileInfo

CHUNK_SIZE = 65536
HASH_ALGORITHM = "sha256"


def calculate_sha256(file_path: str | Path, chunk_size: int = CHUNK_SIZE) -> str:
    """Return the SHA-256 hex digest of a local file."""
    digest = hashlib.sha256()
    with open(file_path, "rb") as handle:
        _update_from_stream(digest, handle, chunk_size)
    return digest.hexdigest()


def _update_from_stream(digest: hashlib._Hash, handle: BinaryIO, chunk_size: int) -> None:
    while True:
        chunk = handle.read(chunk_size)
        if not chunk:
            break
        digest.update(chunk)


def get_file_info(file_path: str | Path) -> FileInfo:
    path = Path(file_path)
    stats = path.stat()
    return FileInfo(
        path=str(path.resolve()),
        hash=calculate_sha256(path),
        size=stats.st_size,
        last_modified=stats.st_mtime,
    )
