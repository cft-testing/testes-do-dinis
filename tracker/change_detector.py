"""Motor de deteção de mudanças entre snapshots."""

import logging
from datetime import datetime
from typing import Optional

from tracker.models.snapshot import CompanySnapshot
from tracker.models.change import Change, ChangeType

logger = logging.getLogger(__name__)


class ChangeDetector:
    """Compara dois snapshots e identifica mudanças."""

    def detect_changes(
        self, old: CompanySnapshot, new: CompanySnapshot
    ) -> list[Change]:
        """Deteta todas as mudanças entre dois snapshots da mesma empresa."""
        if old.company_id != new.company_id:
            raise ValueError("Snapshots devem ser da mesma empresa")

        changes: list[Change] = []
        timestamp = datetime.now().isoformat()

        changes.extend(self._detect_service_changes(old, new, timestamp))
        changes.extend(self._detect_pricing_changes(old, new, timestamp))
        changes.extend(self._detect_location_changes(old, new, timestamp))
        changes.extend(self._detect_promotion_changes(old, new, timestamp))
        changes.extend(self._detect_business_changes(old, new, timestamp))
        changes.extend(self._detect_page_changes(old, new, timestamp))

        logger.info(
            f"[{new.company_id}] Detetadas {len(changes)} mudanças"
        )
        return changes

    def _detect_service_changes(
        self, old: CompanySnapshot, new: CompanySnapshot, timestamp: str
    ) -> list[Change]:
        changes = []
        old_services = set(old.services)
        new_services = set(new.services)

        for service in new_services - old_services:
            changes.append(Change(
                company_id=new.company_id,
                change_type=ChangeType.SERVICE_ADDED.value,
                category="services",
                description=f"Novo serviço detetado: {service}",
                new_value=service,
                timestamp=timestamp,
                severity="high",
            ))

        for service in old_services - new_services:
            changes.append(Change(
                company_id=new.company_id,
                change_type=ChangeType.SERVICE_REMOVED.value,
                category="services",
                description=f"Serviço removido: {service}",
                old_value=service,
                timestamp=timestamp,
                severity="high",
            ))

        return changes

    def _detect_pricing_changes(
        self, old: CompanySnapshot, new: CompanySnapshot, timestamp: str
    ) -> list[Change]:
        changes = []
        all_keys = set(list(old.pricing.keys()) + list(new.pricing.keys()))

        for key in all_keys:
            old_price = old.pricing.get(key)
            new_price = new.pricing.get(key)

            if old_price is None and new_price is not None:
                changes.append(Change(
                    company_id=new.company_id,
                    change_type=ChangeType.PRICE_CHANGED.value,
                    category="pricing",
                    description=f"Novo preço registado para: {key}",
                    new_value=str(new_price),
                    timestamp=timestamp,
                    severity="medium",
                ))
            elif old_price is not None and new_price is None:
                changes.append(Change(
                    company_id=new.company_id,
                    change_type=ChangeType.PRICE_CHANGED.value,
                    category="pricing",
                    description=f"Preço removido para: {key}",
                    old_value=str(old_price),
                    timestamp=timestamp,
                    severity="medium",
                ))
            elif old_price != new_price:
                changes.append(Change(
                    company_id=new.company_id,
                    change_type=ChangeType.PRICE_CHANGED.value,
                    category="pricing",
                    description=f"Preço alterado para {key}: {old_price} -> {new_price}",
                    old_value=str(old_price),
                    new_value=str(new_price),
                    timestamp=timestamp,
                    severity="high",
                ))

        return changes

    def _detect_location_changes(
        self, old: CompanySnapshot, new: CompanySnapshot, timestamp: str
    ) -> list[Change]:
        changes = []
        old_locations = set(old.locations)
        new_locations = set(new.locations)

        for location in new_locations - old_locations:
            changes.append(Change(
                company_id=new.company_id,
                change_type=ChangeType.LOCATION_ADDED.value,
                category="locations",
                description=f"Nova localização: {location}",
                new_value=location,
                timestamp=timestamp,
                severity="high",
            ))

        for location in old_locations - new_locations:
            changes.append(Change(
                company_id=new.company_id,
                change_type=ChangeType.LOCATION_REMOVED.value,
                category="locations",
                description=f"Localização removida: {location}",
                old_value=location,
                timestamp=timestamp,
                severity="medium",
            ))

        return changes

    def _detect_promotion_changes(
        self, old: CompanySnapshot, new: CompanySnapshot, timestamp: str
    ) -> list[Change]:
        changes = []
        old_promos = set(old.promotions)
        new_promos = set(new.promotions)

        for promo in new_promos - old_promos:
            changes.append(Change(
                company_id=new.company_id,
                change_type=ChangeType.PROMOTION_NEW.value,
                category="promotions",
                description=f"Nova promoção: {promo}",
                new_value=promo,
                timestamp=timestamp,
                severity="medium",
            ))

        for promo in old_promos - new_promos:
            changes.append(Change(
                company_id=new.company_id,
                change_type=ChangeType.PROMOTION_EXPIRED.value,
                category="promotions",
                description=f"Promoção expirada/removida: {promo}",
                old_value=promo,
                timestamp=timestamp,
                severity="info",
            ))

        return changes

    def _detect_business_changes(
        self, old: CompanySnapshot, new: CompanySnapshot, timestamp: str
    ) -> list[Change]:
        changes = []
        old_hash = old.business_info.get("about_text_hash", "")
        new_hash = new.business_info.get("about_text_hash", "")

        if old_hash and new_hash and old_hash != new_hash:
            changes.append(Change(
                company_id=new.company_id,
                change_type=ChangeType.BUSINESS_MODEL_CHANGE.value,
                category="business_model",
                description="Conteúdo da página 'Sobre' alterado - possível mudança no modelo de negócio",
                old_value=old.business_info.get("about_text_preview", ""),
                new_value=new.business_info.get("about_text_preview", ""),
                timestamp=timestamp,
                severity="medium",
            ))

        return changes

    def _detect_page_changes(
        self, old: CompanySnapshot, new: CompanySnapshot, timestamp: str
    ) -> list[Change]:
        changes = []
        all_pages = set(list(old.raw_pages.keys()) + list(new.raw_pages.keys()))

        for page in all_pages:
            old_hash = old.raw_pages.get(page, "")
            new_hash = new.raw_pages.get(page, "")

            if old_hash and new_hash and old_hash != new_hash:
                changes.append(Change(
                    company_id=new.company_id,
                    change_type=ChangeType.WEBSITE_CONTENT_CHANGE.value,
                    category="business_model",
                    description=f"Conteúdo da página '{page}' alterado",
                    old_value=f"hash: {old_hash[:16]}...",
                    new_value=f"hash: {new_hash[:16]}...",
                    timestamp=timestamp,
                    severity="info",
                ))

        return changes
