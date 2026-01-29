"""Scraper para o Webel."""

import logging
import re

from bs4 import BeautifulSoup

from tracker.scrapers.base import BaseScraper
from tracker.models.snapshot import CompanySnapshot

logger = logging.getLogger(__name__)


class WebelScraper(BaseScraper):
    """Scraper para o website do Webel."""

    COMPANY_ID = "webel"
    COMPANY_NAME = "Webel"

    URLS = {
        "home": "https://webel.pt",
        "services": "https://webel.pt/servicos",
        "pricing": "https://webel.pt/precos",
        "about": "https://webel.pt/sobre",
        "locations": "https://webel.pt/localizacoes",
    }

    def scrape(self) -> CompanySnapshot:
        """Scrape completo do website Webel."""
        logger.info(f"[{self.COMPANY_ID}] Iniciando scraping do Webel...")
        raw_pages = {}
        parsed_pages = {}

        for page_name, url in self.URLS.items():
            html = self.fetch_page(url)
            if html:
                raw_pages[page_name] = self.content_hash(html)
                parsed_pages[page_name] = self.parse_html(html)

        services = []
        pricing = {}
        locations = []
        promotions = []
        business_info = {}

        if "services" in parsed_pages:
            services = self.extract_services(parsed_pages["services"])
        if "home" in parsed_pages:
            home_services = self.extract_services(parsed_pages["home"])
            services.extend(s for s in home_services if s not in services)
            promotions = self.extract_promotions(parsed_pages["home"])

        if "pricing" in parsed_pages:
            pricing = self.extract_pricing(parsed_pages["pricing"])

        if "locations" in parsed_pages:
            locations = self.extract_locations(parsed_pages["locations"])

        if "about" in parsed_pages:
            texts = self.extract_text_blocks(parsed_pages["about"])
            if texts:
                business_info["about_text_hash"] = self.content_hash("\n".join(texts))
                business_info["about_text_preview"] = " ".join(texts[:5])[:500]

        return self._build_snapshot(
            services=services,
            pricing=pricing,
            locations=locations,
            promotions=promotions,
            business_info=business_info,
            raw_pages=raw_pages,
        )

    def extract_services(self, soup: BeautifulSoup) -> list[str]:
        """Extrai serviços do Webel."""
        services = []

        for selector in [
            ".service", ".servico", ".service-card", "[class*=service]",
            "[class*=servico]", ".card",
        ]:
            for el in soup.select(selector):
                heading = el.find(["h2", "h3", "h4"])
                if heading:
                    text = heading.get_text(strip=True)
                    if text and text not in services:
                        services.append(text)

        if not services:
            for el in soup.find_all(["h2", "h3"]):
                text = el.get_text(strip=True).lower()
                if any(kw in text for kw in ["serviço", "servico", "service"]):
                    parent = el.parent
                    if parent:
                        for item in parent.find_all("li"):
                            services.append(item.get_text(strip=True))

        return services

    def extract_pricing(self, soup: BeautifulSoup) -> dict:
        """Extrai informação de preços do Webel."""
        pricing = {}
        price_pattern = re.compile(r"(\d+[.,]?\d*)\s*€")

        for card in soup.select("[class*=price], [class*=preco], [class*=plan], .card"):
            title = card.find(["h2", "h3", "h4"])
            price_el = card.find(text=price_pattern)
            if title and price_el:
                match = price_pattern.search(price_el)
                if match:
                    pricing[title.get_text(strip=True)] = match.group(0)

        if not pricing:
            for table in soup.find_all("table"):
                for row in table.find_all("tr")[1:]:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 2:
                        pricing[cells[0].get_text(strip=True)] = cells[1].get_text(strip=True)

        return pricing

    def extract_locations(self, soup: BeautifulSoup) -> list[str]:
        """Extrai localizações do Webel."""
        locations = []
        for selector in [".location", ".city", ".cidade", "[class*=location]", "[class*=cidade]"]:
            for el in soup.select(selector):
                text = el.get_text(strip=True)
                if text and text not in locations:
                    locations.append(text)

        if not locations:
            for el in soup.find_all(["h2", "h3"]):
                text = el.get_text(strip=True).lower()
                if any(kw in text for kw in ["localiza", "cidade", "zona", "onde"]):
                    sibling = el.find_next_sibling()
                    if sibling:
                        for li in sibling.find_all("li"):
                            locations.append(li.get_text(strip=True))

        return locations

    def extract_promotions(self, soup: BeautifulSoup) -> list[str]:
        """Extrai promoções do Webel."""
        promotions = []
        discount_pattern = re.compile(r"\d+%|desc(onto)?|cupão|oferta|grátis|promoção", re.I)

        for selector in ["[class*=promo]", "[class*=discount]", "[class*=desconto]", ".banner"]:
            for el in soup.select(selector):
                text = el.get_text(strip=True)
                if text and len(text) < 300:
                    promotions.append(text)

        for el in soup.find_all(text=discount_pattern):
            parent = el.parent
            if parent:
                text = parent.get_text(strip=True)
                if text and text not in promotions and len(text) < 300:
                    promotions.append(text)

        return promotions
