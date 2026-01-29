"""Modelo de mudança detetada entre dois snapshots."""

import json
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional


class ChangeType(Enum):
    SERVICE_ADDED = "service_added"
    SERVICE_REMOVED = "service_removed"
    PRICE_CHANGED = "price_changed"
    LOCATION_ADDED = "location_added"
    LOCATION_REMOVED = "location_removed"
    PROMOTION_NEW = "promotion_new"
    PROMOTION_EXPIRED = "promotion_expired"
    BUSINESS_MODEL_CHANGE = "business_model_change"
    WEBSITE_CONTENT_CHANGE = "website_content_change"

    @property
    def label_pt(self) -> str:
        labels = {
            "service_added": "Novo Serviço",
            "service_removed": "Serviço Removido",
            "price_changed": "Alteração de Preço",
            "location_added": "Nova Localização",
            "location_removed": "Localização Removida",
            "promotion_new": "Nova Promoção",
            "promotion_expired": "Promoção Expirada",
            "business_model_change": "Mudança no Modelo de Negócio",
            "website_content_change": "Alteração de Conteúdo no Website",
        }
        return labels.get(self.value, self.value)


@dataclass
class Change:
    """Uma mudança detetada entre dois snapshots."""

    company_id: str
    change_type: str
    category: str
    description: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    timestamp: str = ""
    severity: str = "info"  # info, medium, high

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "Change":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @property
    def severity_emoji(self) -> str:
        return {"info": "ℹ️", "medium": "⚠️", "high": "🔴"}.get(self.severity, "ℹ️")

    @property
    def type_label(self) -> str:
        try:
            return ChangeType(self.change_type).label_pt
        except ValueError:
            return self.change_type
