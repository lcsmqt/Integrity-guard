from src.compare import compare_baselines
from src.models import FileInfo


def _info(path: str, digest: str) -> FileInfo:
    return FileInfo(path=path, hash=digest, size=10, last_modified=1.0)


def test_compare_detects_added_modified_deleted_and_unchanged() -> None:
    baseline = [
        _info("/a.txt", "aaa"),
        _info("/b.txt", "bbb"),
        _info("/c.txt", "ccc"),
    ]
    current = [
        _info("/a.txt", "aaa"),
        _info("/b.txt", "changed"),
        _info("/d.txt", "ddd"),
    ]
    result = compare_baselines(current, baseline)
    assert [item.path for item in result.added] == ["/d.txt"]
    assert [item.path for item in result.modified] == ["/b.txt"]
    assert [item.path for item in result.deleted] == ["/c.txt"]
    assert [item.path for item in result.unchanged] == ["/a.txt"]
    assert result.has_changes is True
    assert result.summary == {"added": 1, "modified": 1, "deleted": 1, "unchanged": 1}


def test_compare_no_changes() -> None:
    files = [_info("/ok.txt", "same")]
    result = compare_baselines(files, files)
    assert result.has_changes is False
    assert result.summary["unchanged"] == 1
