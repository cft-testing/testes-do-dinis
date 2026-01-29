"""Modelo de snapshot - captura do estado de uma empresa num dado momento."""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class CompanySnapshot:
    """Captura do estado de uma empresa num dado momento."""

    company_id: str
    timestamp: str = ""
    services: list[str] = field(default_factory=list)
    pricing: dict = field(default_factory=dict)
    locations: list[str] = field(default_factory=list)
    promotions: list[str] = field(default_factory=list)
    business_info: dict = field(default_factory=dict)
    raw_pages: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "CompanySnapshot":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, json_str: str) -> "CompanySnapshot":
        return cls.from_dict(json.loads(json_str))

    def save(self, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def load(cls, filepath: str) -> "CompanySnapshot":
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())
