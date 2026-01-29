"""Scraper para o FIXO (a nossa empresa)."""

import logging
import re

from bs4 import BeautifulSoup

from tracker.scrapers.base import BaseScraper
from tracker.models.snapshot import CompanySnapshot

logger = logging.getLogger(__name__)


class FixoScraper(BaseScraper):
    """Scraper para o website do FIXO."""

    COMPANY_ID = "fixo"
    COMPANY_NAME = "FIXO"

    URLS = {
        "home": "https://fixo.pt",
        "services": "https://fixo.pt/servicos",
        "pricing": "https://fixo.pt/precos",
        "about": "https://fixo.pt/sobre",
        "blog": "https://fixo.pt/blog",
        "locations": "https://fixo.pt/localizacoes",
    }

    def scrape(self) -> CompanySnapshot:
        """Scrape completo do website FIXO."""
        logger.info(f"[{self.COMPANY_ID}] Iniciando scraping do FIXO...")
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
            services.extend(self.extract_services(parsed_pages["home"]))
            promotions = self.extract_promotions(parsed_pages["home"])
            services = list(dict.fromkeys(services))  # deduplicate keeping order

        if "pricing" in parsed_pages:
            pricing = self.extract_pricing(parsed_pages["pricing"])

        if "locations" in parsed_pages:
            locations = self.extract_locations(parsed_pages["locations"])

        if "about" in parsed_pages:
            business_info = self._extract_business_info(parsed_pages["about"])

        snapshot = self._build_snapshot(
            services=services,
            pricing=pricing,
            locations=locations,
            promotions=promotions,
            business_info=business_info,
            raw_pages=raw_pages,
        )
        logger.info(f"[{self.COMPANY_ID}] Snapshot criado: {len(services)} serviços, {len(locations)} localizações")
        return snapshot

    def extract_services(self, soup: BeautifulSoup) -> list[str]:
        """Extrai serviços do FIXO."""
        services = []
        # Procura por cards de serviço, listas, títulos com padrões comuns
        for selector in [
            "div.service", "div.servico", ".service-card", ".service-item",
            "li.service", "a.service-link", "[data-service]",
        ]:
            for el in soup.select(selector):
                text = el.get_text(strip=True)
                if text and len(text) < 200:
                    services.append(text)

        # Fallback: procurar headings em secções de serviços
        if not services:
            for section in soup.find_all(["section", "div"], class_=re.compile(r"servic|service", re.I)):
                for heading in section.find_all(["h2", "h3", "h4"]):
                    text = heading.get_text(strip=True)
                    if text:
                        services.append(text)

        # Fallback: procurar por listas genéricas dentro de secções relevantes
        if not services:
            for el in soup.find_all(["h2", "h3"]):
                text = el.get_text(strip=True).lower()
                if any(kw in text for kw in ["serviço", "servico", "service", "o que fazemos"]):
                    sibling = el.find_next_sibling()
                    if sibling:
                        for li in sibling.find_all("li"):
                            services.append(li.get_text(strip=True))

        return services

    def extract_pricing(self, soup: BeautifulSoup) -> dict:
        """Extrai informação de preços do FIXO."""
        pricing = {}

        # Procura tabelas de preços
        for table in soup.find_all("table"):
            rows = table.find_all("tr")
            for row in rows[1:]:  # skip header
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    service = cells[0].get_text(strip=True)
                    price = cells[1].get_text(strip=True)
                    if service and price:
                        pricing[service] = price

        # Procura cards de pricing
        if not pricing:
            for card in soup.select(".pricing-card, .price-card, .plan, .plano, [class*=price], [class*=preco]"):
                title = card.find(["h2", "h3", "h4", ".title", ".name"])
                price_el = card.find(class_=re.compile(r"price|preco|valor", re.I))
                if title and price_el:
                    pricing[title.get_text(strip=True)] = price_el.get_text(strip=True)

        # Fallback: procurar padrões de preço no texto
        if not pricing:
            price_pattern = re.compile(r"(\d+[.,]?\d*)\s*€")
            for el in soup.find_all(text=price_pattern):
                parent = el.parent
                if parent:
                    full_text = parent.get_text(strip=True)
                    match = price_pattern.search(full_text)
                    if match:
                        pricing[full_text[:80]] = match.group(0)

        return pricing

    def extract_locations(self, soup: BeautifulSoup) -> list[str]:
        """Extrai localizações do FIXO."""
        locations = []

        for selector in [
            ".location", ".localizacao", ".city", ".cidade",
            "li.location", "[data-location]", "[data-city]",
        ]:
            for el in soup.select(selector):
                text = el.get_text(strip=True)
                if text:
                    locations.append(text)

        # Fallback: procurar em listas genéricas
        if not locations:
            for el in soup.find_all(["h2", "h3"]):
                text = el.get_text(strip=True).lower()
                if any(kw in text for kw in ["localiza", "cidade", "zona", "onde", "location"]):
                    sibling = el.find_next_sibling()
                    if sibling:
                        for li in sibling.find_all("li"):
                            locations.append(li.get_text(strip=True))

        return locations

    def extract_promotions(self, soup: BeautifulSoup) -> list[str]:
        """Extrai promoções e cupões do FIXO."""
        promotions = []

        for selector in [
            ".promo", ".promotion", ".desconto", ".coupon", ".cupao",
            ".banner-promo", "[class*=promo]", "[class*=discount]",
            "[class*=desconto]", "[class*=coupon]",
        ]:
            for el in soup.select(selector):
                text = el.get_text(strip=True)
                if text and len(text) < 300:
                    promotions.append(text)

        # Procurar por padrões de desconto no texto
        discount_pattern = re.compile(r"\d+%\s*(de\s+)?desc(onto)?|cupão|coupon|oferta|grátis|free", re.I)
        for el in soup.find_all(text=discount_pattern):
            parent = el.parent
            if parent:
                text = parent.get_text(strip=True)
                if text and text not in promotions and len(text) < 300:
                    promotions.append(text)

        return promotions

    def _extract_business_info(self, soup: BeautifulSoup) -> dict:
        """Extrai informação sobre o modelo de negócio."""
        info = {}
        texts = self.extract_text_blocks(soup)
        if texts:
            info["about_text_hash"] = self.content_hash("\n".join(texts))
            info["about_text_preview"] = " ".join(texts[:5])[:500]
        return info
