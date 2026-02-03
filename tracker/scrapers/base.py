"""Scraper base com funcionalidade comum a todos os scrapers."""

import hashlib
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional

import requests
from bs4 import BeautifulSoup

from tracker.models.snapshot import CompanySnapshot

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Classe base para scrapers de empresas."""

    COMPANY_ID: str = ""
    COMPANY_NAME: str = ""

    def __init__(self, config: dict):
        self.config = config
        scraping_cfg = config.get("scraping", {})
        self.timeout = scraping_cfg.get("request_timeout_seconds", 30)
        self.delay = scraping_cfg.get("delay_between_requests_seconds", 2)
        self.max_retries = scraping_cfg.get("max_retries", 3)
        self.user_agent = scraping_cfg.get("user_agent", "FIXO-CompetitiveIntel/1.0")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def fetch_page(self, url: str) -> Optional[str]:
        """Faz fetch de uma página com retries e delay."""
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"[{self.COMPANY_ID}] Fetching {url} (tentativa {attempt})")
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                time.sleep(self.delay)
                return response.text
            except requests.RequestException as e:
                logger.warning(f"[{self.COMPANY_ID}] Erro ao aceder {url}: {e}")
                if attempt < self.max_retries:
                    wait = 2 ** attempt
                    logger.info(f"[{self.COMPANY_ID}] Aguardar {wait}s antes de retry...")
                    time.sleep(wait)
        return None

    def parse_html(self, html: str) -> BeautifulSoup:
        """Faz parse de HTML para BeautifulSoup."""
        return BeautifulSoup(html, "lxml")

    def content_hash(self, content: str) -> str:
        """Gera hash de conteúdo para deteção rápida de mudanças."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def extract_text_blocks(self, soup: BeautifulSoup) -> list[str]:
        """Extrai blocos de texto relevantes de uma página."""
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        texts = []
        for element in soup.find_all(["p", "h1", "h2", "h3", "h4", "li", "span", "div"]):
            text = element.get_text(strip=True)
            if text and len(text) > 10:
                texts.append(text)
        return texts

    @abstractmethod
    def scrape(self) -> CompanySnapshot:
        """Executa o scraping completo e retorna um snapshot."""
        ...

    @abstractmethod
    def extract_services(self, soup: BeautifulSoup) -> list[str]:
        """Extrai a lista de serviços oferecidos."""
        ...

    @abstractmethod
    def extract_pricing(self, soup: BeautifulSoup) -> dict:
        """Extrai informação de preços."""
        ...

    @abstractmethod
    def extract_locations(self, soup: BeautifulSoup) -> list[str]:
        """Extrai as localizações onde opera."""
        ...

    @abstractmethod
    def extract_promotions(self, soup: BeautifulSoup) -> list[str]:
        """Extrai promoções/cupões ativos."""
        ...

    def _build_snapshot(
        self,
        services: list[str],
        pricing: dict,
        locations: list[str],
        promotions: list[str],
        business_info: dict,
        raw_pages: dict,
    ) -> CompanySnapshot:
        """Constrói um snapshot com os dados extraídos."""
        return CompanySnapshot(
            company_id=self.COMPANY_ID,
            services=services,
            pricing=pricing,
            locations=locations,
            promotions=promotions,
            business_info=business_info,
            raw_pages=raw_pages,
        )
