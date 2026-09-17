from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

from src.compare import compare_baselines
from src.config import load_config
from src.logging_setup import setup_logging
from src.models import Config, ScanResult
from src.reporting import write_reports
from src.scanner import scan_paths
from src.store import FileStore

logger = logging.getLogger("file_integrity_guard")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description="Monitor defensivo de integridade de arquivos (FIM) com baseline SHA-256.",
    )
    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Caminho do arquivo YAML de configuração (padrão: config/config.yaml).",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Cria ou substitui a linha de base autorizada.")
    init_parser.set_defaults(handler=_handle_init)

    check_parser = subparsers.add_parser("check", help="Compara o estado atual com a linha de base.")
    check_parser.add_argument(
        "--write-report",
        action="store_true",
        help="Também grava relatórios JSON e Markdown.",
    )
    check_parser.set_defaults(handler=_handle_check)

    report_parser = subparsers.add_parser("report", help="Executa a verificação e gera relatórios.")
    report_parser.set_defaults(handler=_handle_report)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config(args.config)
    setup_logging(config.log_level)
    try:
        return int(args.handler(config, args))
    except FileNotFoundError as exc:
        logger.error("%s", exc)
        return 2
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        logger.exception("Falha inesperada: %s", exc)
        return 1


def _handle_init(config: Config, _args: argparse.Namespace) -> int:
    files = scan_paths(config)
    with FileStore(config.db_path) as store:
        count = store.replace_baseline(files)
        store.set_meta("created_at", datetime.now(timezone.utc).isoformat())
        store.set_meta("file_count", str(count))
    print(f"Linha de base criada com {count} arquivo(s) em {config.db_path}")
    return 0


def _handle_check(config: Config, args: argparse.Namespace) -> int:
    result = _run_check(config)
    _print_summary(result)
    if getattr(args, "write_report", False):
        paths = write_reports(result, config.report_dir)
        print(f"Relatórios gravados em {paths['latest_json']} e {paths['latest_markdown']}")
    return 1 if result.has_changes else 0


def _handle_report(config: Config, _args: argparse.Namespace) -> int:
    result = _run_check(config)
    _print_summary(result)
    paths = write_reports(result, config.report_dir)
    print(f"Relatório JSON: {paths['json']}")
    print(f"Relatório Markdown: {paths['markdown']}")
    return 1 if result.has_changes else 0


def _run_check(config: Config) -> ScanResult:
    db_path = Path(config.db_path)
    if not db_path.is_file():
        raise FileNotFoundError(
            f"Linha de base não encontrada em {db_path}. Execute 'python -m src.cli init' primeiro."
        )
    current = scan_paths(config)
    with FileStore(db_path) as store:
        baseline = store.get_all_files()
    if not baseline:
        raise FileNotFoundError("A linha de base está vazia. Execute 'python -m src.cli init' novamente.")
    return compare_baselines(current, baseline)


def _print_summary(result: ScanResult) -> None:
    summary = result.summary
    print("Resumo da verificação:")
    print(f"  adicionados : {summary['added']}")
    print(f"  modificados : {summary['modified']}")
    print(f"  excluídos   : {summary['deleted']}")
    print(f"  inalterados : {summary['unchanged']}")
    _print_group("Adicionados", result.added)
    _print_group("Modificados", result.modified)
    _print_group("Excluídos", result.deleted)


def _print_group(title: str, items) -> None:
    if not items:
        return
    print(f"{title}:")
    for item in items:
        print(f"  - {item.path} ({item.hash[:12]}...)")


if __name__ == "__main__":
    sys.exit(main())
