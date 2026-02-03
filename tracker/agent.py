"""Agente principal de tracking competitivo."""

import json
import logging
from pathlib import Path
from typing import Optional

from tracker.scrapers import SCRAPERS
from tracker.change_detector import ChangeDetector
from tracker.storage import SnapshotStorage
from tracker.reports.generator import ReportGenerator
from tracker.models.snapshot import CompanySnapshot
from tracker.models.change import Change

logger = logging.getLogger(__name__)


class CompetitiveAgent:
    """Agente que coordena o scraping, deteção de mudanças e relatórios."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.settings = self._load_json("settings.json")
        self.companies_config = self._load_json("companies.json")

        storage_cfg = self.settings.get("storage", {})
        self.storage = SnapshotStorage(
            base_dir=storage_cfg.get("snapshots_dir", "data/snapshots"),
            max_per_company=storage_cfg.get("max_snapshots_per_company", 90),
        )
        self.detector = ChangeDetector()
        self.reporter = ReportGenerator(
            reports_dir=storage_cfg.get("reports_dir", "data/reports")
        )

    def _load_json(self, filename: str) -> dict:
        filepath = self.config_dir / filename
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_company_ids(self) -> list[str]:
        """Retorna IDs de todas as empresas configuradas."""
        return [c["id"] for c in self.companies_config.get("companies", [])]

    def run_scan(
        self,
        company_ids: Optional[list[str]] = None,
        report_format: str = "terminal",
    ) -> dict[str, list[Change]]:
        """Executa um scan completo: scraping + deteção de mudanças + relatório."""
        if company_ids is None:
            company_ids = self.get_company_ids()

        logger.info(f"Iniciando scan para: {', '.join(company_ids)}")

        all_changes: dict[str, list[Change]] = {}
        current_snapshots: dict[str, CompanySnapshot] = {}

        for company_id in company_ids:
            try:
                changes, snapshot = self._scan_company(company_id)
                all_changes[company_id] = changes
                if snapshot:
                    current_snapshots[company_id] = snapshot
            except Exception as e:
                logger.error(f"Erro ao processar {company_id}: {e}")
                all_changes[company_id] = []

        # Gerar relatório
        if report_format == "terminal":
            report = self.reporter.generate_terminal_report(all_changes, current_snapshots)
            print(report)
        elif report_format == "markdown":
            report = self.reporter.generate_markdown_report(all_changes, current_snapshots)
            print(report)

        # Guardar relatórios em ficheiro
        saved = self.reporter.save_report(all_changes, current_snapshots)
        if saved:
            logger.info(f"Relatórios guardados: {', '.join(saved)}")

        return all_changes

    def _scan_company(
        self, company_id: str
    ) -> tuple[list[Change], Optional[CompanySnapshot]]:
        """Faz scan de uma empresa individual."""
        scraper_class = SCRAPERS.get(company_id)
        if not scraper_class:
            logger.warning(f"Scraper não encontrado para: {company_id}")
            return [], None

        # Obter snapshot anterior
        previous = self.storage.get_latest_snapshot(company_id)

        # Fazer novo scraping
        scraper = scraper_class(self.settings)
        new_snapshot = scraper.scrape()

        # Guardar novo snapshot
        self.storage.save_snapshot(new_snapshot)

        # Detetar mudanças
        changes = []
        if previous:
            changes = self.detector.detect_changes(previous, new_snapshot)
            logger.info(
                f"[{company_id}] {len(changes)} mudanças detetadas vs snapshot anterior"
            )
        else:
            logger.info(
                f"[{company_id}] Primeiro snapshot - sem dados anteriores para comparação"
            )

        return changes, new_snapshot

    def get_company_status(self, company_id: str) -> Optional[dict]:
        """Retorna o estado atual de uma empresa."""
        snapshot = self.storage.get_latest_snapshot(company_id)
        if not snapshot:
            return None

        return {
            "company_id": company_id,
            "last_scan": snapshot.timestamp,
            "services_count": len(snapshot.services),
            "services": snapshot.services,
            "locations_count": len(snapshot.locations),
            "locations": snapshot.locations,
            "pricing": snapshot.pricing,
            "promotions": snapshot.promotions,
            "business_info": snapshot.business_info,
        }

    def get_all_status(self) -> dict:
        """Retorna estado de todas as empresas."""
        status = {}
        for company_id in self.get_company_ids():
            status[company_id] = self.get_company_status(company_id)
        return status
