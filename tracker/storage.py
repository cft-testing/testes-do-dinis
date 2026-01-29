"""Gestão de armazenamento de snapshots e dados históricos."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from tracker.models.snapshot import CompanySnapshot

logger = logging.getLogger(__name__)


class SnapshotStorage:
    """Armazena e recupera snapshots de empresas."""

    def __init__(self, base_dir: str = "data/snapshots", max_per_company: int = 90):
        self.base_dir = Path(base_dir)
        self.max_per_company = max_per_company
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _company_dir(self, company_id: str) -> Path:
        path = self.base_dir / company_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_snapshot(self, snapshot: CompanySnapshot) -> str:
        """Guarda um snapshot e retorna o caminho do ficheiro."""
        company_dir = self._company_dir(snapshot.company_id)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{snapshot.company_id}_{timestamp}.json"
        filepath = company_dir / filename

        snapshot.save(str(filepath))
        logger.info(f"Snapshot guardado: {filepath}")

        self._cleanup_old_snapshots(snapshot.company_id)
        return str(filepath)

    def get_latest_snapshot(self, company_id: str) -> Optional[CompanySnapshot]:
        """Retorna o snapshot mais recente de uma empresa."""
        company_dir = self._company_dir(company_id)
        files = sorted(company_dir.glob(f"{company_id}_*.json"), reverse=True)

        if not files:
            return None

        return CompanySnapshot.load(str(files[0]))

    def get_previous_snapshot(self, company_id: str) -> Optional[CompanySnapshot]:
        """Retorna o penúltimo snapshot (para comparação)."""
        company_dir = self._company_dir(company_id)
        files = sorted(company_dir.glob(f"{company_id}_*.json"), reverse=True)

        if len(files) < 2:
            return None

        return CompanySnapshot.load(str(files[1]))

    def get_all_snapshots(self, company_id: str) -> list[CompanySnapshot]:
        """Retorna todos os snapshots de uma empresa, do mais recente para o mais antigo."""
        company_dir = self._company_dir(company_id)
        files = sorted(company_dir.glob(f"{company_id}_*.json"), reverse=True)
        return [CompanySnapshot.load(str(f)) for f in files]

    def _cleanup_old_snapshots(self, company_id: str):
        """Remove snapshots antigos se exceder o limite."""
        company_dir = self._company_dir(company_id)
        files = sorted(company_dir.glob(f"{company_id}_*.json"), reverse=True)

        if len(files) > self.max_per_company:
            for f in files[self.max_per_company:]:
                f.unlink()
                logger.info(f"Snapshot antigo removido: {f}")
