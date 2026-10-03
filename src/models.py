from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FileInfo:
    path: str
    hash: str
    size: int
    last_modified: float


@dataclass
class ScanResult:
    added: list[FileInfo] = field(default_factory=list)
    modified: list[FileInfo] = field(default_factory=list)
    deleted: list[FileInfo] = field(default_factory=list)
    unchanged: list[FileInfo] = field(default_factory=list)

    @property
    def summary(self) -> dict[str, int]:
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
    paths: list[str]
    include: list[str]
    exclude: list[str]
    db_path: str
    report_dir: str
    log_level: str
    follow_symlinks: bool = False


@dataclass
class Report:
    timestamp: str
    scan_result: ScanResult
    summary: dict[str, int]


@dataclass
class ThreatModel:
    description: str
    mitigations: list[str]
    vulnerabilities: list[str]
    residual_risks: list[str] | None = None
