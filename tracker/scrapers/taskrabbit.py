"""Scraper para o TaskRabbit."""

import logging
import re

from bs4 import BeautifulSoup

from tracker.scrapers.base import BaseScraper
from tracker.models.snapshot import CompanySnapshot

logger = logging.getLogger(__name__)


class TaskRabbitScraper(BaseScraper):
    """Scraper para o website do TaskRabbit."""

    COMPANY_ID = "taskrabbit"
    COMPANY_NAME = "TaskRabbit"

    URLS = {
        "home": "https://www.taskrabbit.com",
        "services": "https://www.taskrabbit.com/services",
        "locations": "https://www.taskrabbit.com/locations",
        "about": "https://www.taskrabbit.com/about",
        "pricing": "https://www.taskrabbit.com/how-it-works",
    }

    def scrape(self) -> CompanySnapshot:
        """Scrape completo do website TaskRabbit."""
        logger.info(f"[{self.COMPANY_ID}] Iniciando scraping do TaskRabbit...")
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
        """Extrai serviços do TaskRabbit."""
        services = []

        # TaskRabbit usa cards e grelhas de serviços
        for selector in [
            ".task-category", ".category-card", ".service-card",
            "[class*=category]", "[class*=service]", ".card",
            "a[href*='/services/']",
        ]:
            for el in soup.select(selector):
                heading = el.find(["h2", "h3", "h4", "span", "p"])
                if heading:
                    text = heading.get_text(strip=True)
                    if text and text not in services and len(text) < 100:
                        services.append(text)

        # Fallback: links de serviços
        if not services:
            for link in soup.find_all("a", href=re.compile(r"/services/")):
                text = link.get_text(strip=True)
                if text and text not in services and len(text) < 100:
                    services.append(text)

        return services

    def extract_pricing(self, soup: BeautifulSoup) -> dict:
        """Extrai informação de preços do TaskRabbit."""
        pricing = {}
        price_pattern = re.compile(r"[\$€£]\s*(\d+[.,]?\d*)")

        for card in soup.select("[class*=price], [class*=rate], [class*=cost], .card"):
            title = card.find(["h2", "h3", "h4"])
            price_text = card.find(text=price_pattern)
            if title and price_text:
                match = price_pattern.search(price_text)
                if match:
                    pricing[title.get_text(strip=True)] = match.group(0)

        # Procurar menções de preço/hora no texto geral
        if not pricing:
            for el in soup.find_all(text=re.compile(r"(per hour|por hora|/hr|/h)", re.I)):
                parent = el.parent
                if parent:
                    text = parent.get_text(strip=True)
                    match = price_pattern.search(text)
                    if match:
                        pricing[text[:60]] = match.group(0)

        return pricing

    def extract_locations(self, soup: BeautifulSoup) -> list[str]:
        """Extrai localizações do TaskRabbit."""
        locations = []

        for selector in [
            ".city", ".location", "[class*=city]", "[class*=location]",
            "a[href*='/locations/']",
        ]:
            for el in soup.select(selector):
                text = el.get_text(strip=True)
                if text and text not in locations and len(text) < 100:
                    locations.append(text)

        if not locations:
            for link in soup.find_all("a", href=re.compile(r"/locations/")):
                text = link.get_text(strip=True)
                if text and text not in locations and len(text) < 100:
                    locations.append(text)

        return locations

    def extract_promotions(self, soup: BeautifulSoup) -> list[str]:
        """Extrai promoções do TaskRabbit."""
        promotions = []
        promo_pattern = re.compile(r"\d+%\s*off|discount|promo|coupon|free|deal", re.I)

        for selector in ["[class*=promo]", "[class*=discount]", "[class*=offer]", ".banner", "[class*=banner]"]:
            for el in soup.select(selector):
                text = el.get_text(strip=True)
                if text and len(text) < 300:
                    promotions.append(text)

        for el in soup.find_all(text=promo_pattern):
            parent = el.parent
            if parent:
                text = parent.get_text(strip=True)
                if text and text not in promotions and len(text) < 300:
                    promotions.append(text)

        return promotions
