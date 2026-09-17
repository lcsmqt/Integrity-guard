from __future__ import annotations

from typing import Iterable, Mapping

from src.models import FileInfo, ScanResult


def compare_baselines(
    current_files: Iterable[FileInfo],
    baseline_files: Iterable[FileInfo],
) -> ScanResult:
    current = {item.path: item for item in current_files}
    baseline = {item.path: item for item in baseline_files}
    return compare_maps(current, baseline)


def compare_maps(
    current: Mapping[str, FileInfo],
    baseline: Mapping[str, FileInfo],
) -> ScanResult:
    result = ScanResult()
    current_paths = set(current)
    baseline_paths = set(baseline)

    for path in sorted(current_paths - baseline_paths):
        result.added.append(current[path])

    for path in sorted(baseline_paths - current_paths):
        result.deleted.append(baseline[path])

    for path in sorted(current_paths & baseline_paths):
        current_item = current[path]
        baseline_item = baseline[path]
        if current_item.hash != baseline_item.hash:
            result.modified.append(current_item)
        else:
            result.unchanged.append(current_item)

    return result
