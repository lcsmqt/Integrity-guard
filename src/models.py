from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FileInfo:
    path: str
    hash: str
    size: int
    last_modified: float


@dataclass
class ScanResult:
    added: List[FileInfo] = field(default_factory=list)
    modified: List[FileInfo] = field(default_factory=list)
    deleted: List[FileInfo] = field(default_factory=list)
    unchanged: List[FileInfo] = field(default_factory=list)

    @property
    def summary(self) -> Dict[str, int]:
        return {
            "added": len(self.added),
            "modified": len(self.modified),
            "deleted": len(self.deleted),
            "unchanged": len(self.unchanged),
        }

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.modified or self.deleted)


@dataclass
class Config:
    paths: List[str]
    include: List[str]
    exclude: List[str]
    db_path: str
    report_dir: str
    log_level: str
    follow_symlinks: bool = False


@dataclass
class Report:
    timestamp: str
    scan_result: ScanResult
    summary: Dict[str, int]


@dataclass
class ThreatModel:
    description: str
    mitigations: List[str]
    vulnerabilities: List[str]
    residual_risks: Optional[List[str]] = None
