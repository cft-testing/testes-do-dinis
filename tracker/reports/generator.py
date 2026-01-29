"""Gerador de relatórios de mudanças competitivas."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from tracker.models.change import Change, ChangeType
from tracker.models.snapshot import CompanySnapshot

logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "services": "Serviços",
    "pricing": "Preços",
    "locations": "Localizações",
    "promotions": "Promoções",
    "business_model": "Modelo de Negócio",
}

SEVERITY_ICONS = {
    "high": "[!!!]",
    "medium": "[!!]",
    "info": "[i]",
}


class ReportGenerator:
    """Gera relatórios em diferentes formatos."""

    def __init__(self, reports_dir: str = "data/reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_terminal_report(
        self,
        changes_by_company: dict[str, list[Change]],
        snapshots: dict[str, CompanySnapshot],
    ) -> str:
        """Gera relatório formatado para terminal."""
        lines = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines.append("=" * 70)
        lines.append("  FIXO - Relatório de Inteligência Competitiva")
        lines.append(f"  Gerado em: {now}")
        lines.append("=" * 70)
        lines.append("")

        total_changes = sum(len(c) for c in changes_by_company.values())
        lines.append(f"  Total de mudanças detetadas: {total_changes}")
        lines.append("")

        if total_changes == 0:
            lines.append("  Nenhuma mudança detetada desde a última verificação.")
            lines.append("=" * 70)
            return "\n".join(lines)

        # Resumo por empresa
        lines.append("-" * 70)
        lines.append("  RESUMO POR EMPRESA")
        lines.append("-" * 70)
        for company_id, changes in changes_by_company.items():
            if changes:
                high = sum(1 for c in changes if c.severity == "high")
                medium = sum(1 for c in changes if c.severity == "medium")
                info = sum(1 for c in changes if c.severity == "info")
                lines.append(
                    f"  {company_id.upper():15s} | "
                    f"{len(changes):3d} mudanças  "
                    f"({high} criticas, {medium} medias, {info} info)"
                )
        lines.append("")

        # Detalhes por empresa
        for company_id, changes in changes_by_company.items():
            if not changes:
                continue

            snapshot = snapshots.get(company_id)
            lines.append("-" * 70)
            lines.append(f"  {company_id.upper()}")
            lines.append("-" * 70)

            if snapshot:
                lines.append(f"  Serviços atuais: {len(snapshot.services)}")
                lines.append(f"  Localizações: {len(snapshot.locations)}")
                lines.append(f"  Preços registados: {len(snapshot.pricing)}")
                lines.append(f"  Promoções ativas: {len(snapshot.promotions)}")
                lines.append("")

            # Agrupar por categoria
            by_category: dict[str, list[Change]] = {}
            for change in changes:
                by_category.setdefault(change.category, []).append(change)

            for category, cat_changes in by_category.items():
                label = CATEGORY_LABELS.get(category, category)
                lines.append(f"  [{label}]")
                for change in cat_changes:
                    icon = SEVERITY_ICONS.get(change.severity, "[i]")
                    lines.append(f"    {icon} {change.description}")
                    if change.old_value and change.new_value:
                        lines.append(f"        Antes: {change.old_value[:80]}")
                        lines.append(f"        Agora: {change.new_value[:80]}")
                lines.append("")

        lines.append("=" * 70)
        lines.append("  Fim do relatório")
        lines.append("=" * 70)

        return "\n".join(lines)

    def generate_markdown_report(
        self,
        changes_by_company: dict[str, list[Change]],
        snapshots: dict[str, CompanySnapshot],
    ) -> str:
        """Gera relatório em Markdown."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = []

        lines.append("# FIXO - Relatório de Inteligência Competitiva")
        lines.append(f"\n**Data:** {now}\n")

        total_changes = sum(len(c) for c in changes_by_company.values())
        lines.append(f"**Total de mudanças detetadas:** {total_changes}\n")

        if total_changes == 0:
            lines.append("Nenhuma mudança detetada desde a última verificação.\n")
            return "\n".join(lines)

        # Tabela resumo
        lines.append("## Resumo\n")
        lines.append("| Empresa | Mudanças | Criticas | Médias | Info |")
        lines.append("|---------|----------|----------|--------|------|")
        for company_id, changes in changes_by_company.items():
            if changes:
                high = sum(1 for c in changes if c.severity == "high")
                medium = sum(1 for c in changes if c.severity == "medium")
                info = sum(1 for c in changes if c.severity == "info")
                lines.append(
                    f"| {company_id.upper()} | {len(changes)} | {high} | {medium} | {info} |"
                )
        lines.append("")

        # Detalhes
        for company_id, changes in changes_by_company.items():
            if not changes:
                continue

            snapshot = snapshots.get(company_id)
            lines.append(f"## {company_id.upper()}\n")

            if snapshot:
                lines.append(f"- **Serviços atuais:** {len(snapshot.services)}")
                lines.append(f"- **Localizações:** {len(snapshot.locations)}")
                lines.append(f"- **Preços registados:** {len(snapshot.pricing)}")
                lines.append(f"- **Promoções ativas:** {len(snapshot.promotions)}")
                lines.append("")

            by_category: dict[str, list[Change]] = {}
            for change in changes:
                by_category.setdefault(change.category, []).append(change)

            for category, cat_changes in by_category.items():
                label = CATEGORY_LABELS.get(category, category)
                lines.append(f"### {label}\n")
                for change in cat_changes:
                    severity_marker = {"high": "**CRITICO**", "medium": "MEDIO", "info": "info"}.get(
                        change.severity, ""
                    )
                    lines.append(f"- [{severity_marker}] {change.description}")
                    if change.old_value and change.new_value:
                        lines.append(f"  - Antes: `{change.old_value[:100]}`")
                        lines.append(f"  - Agora: `{change.new_value[:100]}`")
                lines.append("")

        return "\n".join(lines)

    def generate_json_report(
        self,
        changes_by_company: dict[str, list[Change]],
        snapshots: dict[str, CompanySnapshot],
    ) -> str:
        """Gera relatório em JSON."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_changes": sum(len(c) for c in changes_by_company.values()),
            "companies": {},
        }

        for company_id, changes in changes_by_company.items():
            snapshot = snapshots.get(company_id)
            report["companies"][company_id] = {
                "changes_count": len(changes),
                "changes": [c.to_dict() for c in changes],
                "current_snapshot": snapshot.to_dict() if snapshot else None,
            }

        return json.dumps(report, ensure_ascii=False, indent=2)

    def save_report(
        self,
        changes_by_company: dict[str, list[Change]],
        snapshots: dict[str, CompanySnapshot],
        formats: list[str] = None,
    ) -> list[str]:
        """Guarda relatórios nos formatos especificados. Retorna caminhos dos ficheiros."""
        if formats is None:
            formats = ["markdown", "json"]

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = []

        if "markdown" in formats:
            content = self.generate_markdown_report(changes_by_company, snapshots)
            path = self.reports_dir / f"report_{timestamp}.md"
            path.write_text(content, encoding="utf-8")
            saved_files.append(str(path))

        if "json" in formats:
            content = self.generate_json_report(changes_by_company, snapshots)
            path = self.reports_dir / f"report_{timestamp}.json"
            path.write_text(content, encoding="utf-8")
            saved_files.append(str(path))

        return saved_files
