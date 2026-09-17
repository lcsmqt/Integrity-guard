from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from src.models import FileInfo, ScanResult


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_report_payload(result: ScanResult, generated_at: str | None = None) -> Dict[str, Any]:
    timestamp = generated_at or utc_now_iso()
    return {
        "generated_at": timestamp,
        "summary": result.summary,
        "has_changes": result.has_changes,
        "added": [_file_to_dict(item) for item in result.added],
        "modified": [_file_to_dict(item) for item in result.modified],
        "deleted": [_file_to_dict(item) for item in result.deleted],
        "unchanged": [_file_to_dict(item) for item in result.unchanged],
    }


def write_json_report(result: ScanResult, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_report_payload(result)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_markdown_report(result: ScanResult, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_report_payload(result)
    path.write_text(_render_markdown(payload), encoding="utf-8")
    return path


def write_reports(result: ScanResult, report_dir: str | Path, prefix: str = "integrity-report") -> Dict[str, Path]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    directory = Path(report_dir)
    json_path = write_json_report(result, directory / f"{prefix}-{stamp}.json")
    markdown_path = write_markdown_report(result, directory / f"{prefix}-{stamp}.md")
    latest_json = write_json_report(result, directory / f"{prefix}-latest.json")
    latest_md = write_markdown_report(result, directory / f"{prefix}-latest.md")
    return {
        "json": json_path,
        "markdown": markdown_path,
        "latest_json": latest_json,
        "latest_markdown": latest_md,
    }


def _file_to_dict(item: FileInfo) -> Dict[str, Any]:
    return {
        "path": item.path,
        "hash": item.hash,
        "size": item.size,
        "last_modified": item.last_modified,
    }


def _render_markdown(payload: Dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Relatório de Integridade de Arquivos",
        "",
        f"- Gerado em: `{payload['generated_at']}`",
        f"- Alterações detectadas: {'sim' if payload['has_changes'] else 'não'}",
        "",
        "## Resumo",
        "",
        "| Status | Quantidade |",
        "| --- | ---: |",
        f"| Adicionados | {summary['added']} |",
        f"| Modificados | {summary['modified']} |",
        f"| Excluídos | {summary['deleted']} |",
        f"| Inalterados | {summary['unchanged']} |",
        "",
    ]
    for title, key in (
        ("Arquivos adicionados", "added"),
        ("Arquivos modificados", "modified"),
        ("Arquivos excluídos", "deleted"),
        ("Arquivos inalterados", "unchanged"),
    ):
        items = payload[key]
        lines.append(f"## {title}")
        lines.append("")
        if not items:
            lines.append("Nenhum.")
            lines.append("")
            continue
        lines.append("| Caminho | SHA-256 | Tamanho |")
        lines.append("| --- | --- | ---: |")
        for item in items:
            lines.append(f"| `{item['path']}` | `{item['hash']}` | {item['size']} |")
        lines.append("")
    return "\n".join(lines)
