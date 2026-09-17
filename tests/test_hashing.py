from pathlib import Path

from src.hashing import calculate_sha256, get_file_info


def test_calculate_sha256_known_value(tmp_path: Path) -> None:
    target = tmp_path / "hello.txt"
    target.write_bytes(b"hello")
    assert calculate_sha256(target) == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_get_file_info_includes_size_and_hash(tmp_path: Path) -> None:
    target = tmp_path / "note.txt"
    content = b"integrity"
    target.write_bytes(content)
    info = get_file_info(target)
    assert info.size == len(content)
    assert info.hash == calculate_sha256(target)
    assert Path(info.path).name == "note.txt"
