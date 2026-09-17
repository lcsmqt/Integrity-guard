from pathlib import Path

from src.cli import main


def _write_config(tmp_path: Path) -> Path:
    watch = tmp_path / "watch"
    watch.mkdir()
    (watch / "alpha.txt").write_text("alpha", encoding="utf-8")
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "\n".join(
            [
                f"paths: [{watch.as_posix()!r}]",
                "include: ['**/*']",
                "exclude: []",
                f"db_path: {(tmp_path / 'integrity.db').as_posix()!r}",
                f"report_dir: {(tmp_path / 'reports').as_posix()!r}",
                "log_level: INFO",
            ]
        ),
        encoding="utf-8",
    )
    return config_path


def test_cli_init_check_and_report(tmp_path: Path, capsys) -> None:
    config_path = _write_config(tmp_path)
    assert main(["--config", str(config_path), "init"]) == 0
    assert main(["--config", str(config_path), "check"]) == 0

    watch = tmp_path / "watch"
    (watch / "alpha.txt").write_text("changed", encoding="utf-8")
    (watch / "beta.txt").write_text("new", encoding="utf-8")

    assert main(["--config", str(config_path), "report"]) == 1
    output = capsys.readouterr().out
    assert "modificados : 1" in output
    assert "adicionados : 1" in output
    reports = list((tmp_path / "reports").glob("*.md"))
    assert reports
