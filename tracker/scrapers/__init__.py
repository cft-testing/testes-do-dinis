"""Scrapers para cada empresa monitorizada."""

from tracker.scrapers.base import BaseScraper
from tracker.scrapers.fixo import FixoScraper
from tracker.scrapers.oscar import OscarScraper
from tracker.scrapers.taskrabbit import TaskRabbitScraper
from tracker.scrapers.webel import WebelScraper

SCRAPERS = {
    "fixo": FixoScraper,
    "oscar": OscarScraper,
    "taskrabbit": TaskRabbitScraper,
    "webel": WebelScraper,
}

__all__ = ["BaseScraper", "FixoScraper", "OscarScraper", "TaskRabbitScraper", "WebelScraper", "SCRAPERS"]
