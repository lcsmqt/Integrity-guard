from pathlib import Path

from src.models import FileInfo
from src.store import FileStore


def test_store_roundtrip_and_replace(tmp_path: Path) -> None:
    db_path = tmp_path / "integrity.db"
    first = FileInfo("/tmp/a.txt", "aaa", 1, 1.0)
    second = FileInfo("/tmp/b.txt", "bbb", 2, 2.0)
    with FileStore(db_path) as store:
        store.add_file(first)
        store.set_meta("created_at", "now")
        assert store.get_file("/tmp/a.txt") == first
        count = store.replace_baseline([second])
        assert count == 1
        assert store.get_all_files() == [second]
        assert store.get_meta("created_at") == "now"
