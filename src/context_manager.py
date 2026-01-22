"""
Context Manager Module
Manages historical newsletter data to avoid content repetition
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from difflib import SequenceMatcher


class ContextManager:
    """Manages newsletter history and context to avoid repetitive content"""

    def __init__(self, history_file: str = "data/newsletter_history.json"):
        """
        Initialize the context manager

        Args:
            history_file: Path to the JSON file storing newsletter history
        """
        self.history_file = history_file
        self.history = self._load_history()

    def _load_history(self) -> List[Dict[str, Any]]:
        """Load newsletter history from file"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading history: {e}")
                return []
        return []

    def _save_history(self):
        """Save newsletter history to file"""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def add_newsletter(self, newsletter_data: Dict[str, Any]):
        """
        Add a new newsletter to history

        Args:
            newsletter_data: Dictionary containing newsletter content and metadata
        """
        newsletter_entry = {
            "date": datetime.now().isoformat(),
            "content": newsletter_data
        }
        self.history.insert(0, newsletter_entry)  # Most recent first
        self._save_history()

    def get_recent_newsletters(self, window: int = 8) -> List[Dict[str, Any]]:
        """
        Get recent newsletters within the specified window

        Args:
            window: Number of recent newsletters to retrieve

        Returns:
            List of recent newsletter entries
        """
        return self.history[:window]

    def get_recent_topics(self, days: int = 14) -> List[str]:
        """
        Get topics covered in recent newsletters within the specified time window

        Args:
            days: Number of days to look back

        Returns:
            List of topic titles covered recently
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        topics = []

        for entry in self.history:
            entry_date = datetime.fromisoformat(entry["date"])
            if entry_date < cutoff_date:
                break

            content = entry.get("content", {})
            for section in ["worldwide", "portugal", "ventures"]:
                section_data = content.get(section, [])
                for item in section_data:
                    if "title" in item:
                        topics.append(item["title"])

        return topics

    def get_recent_urls(self, days: int = 14) -> List[str]:
        """
        Get URLs of articles covered in recent newsletters

        Args:
            days: Number of days to look back

        Returns:
            List of article URLs
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        urls = []

        for entry in self.history:
            entry_date = datetime.fromisoformat(entry["date"])
            if entry_date < cutoff_date:
                break

            content = entry.get("content", {})
            for section in ["worldwide", "portugal", "ventures"]:
                section_data = content.get(section, [])
                for item in section_data:
                    if "url" in item:
                        urls.append(item["url"])

        return urls

    def is_similar_content(self, title: str, similarity_threshold: float = 0.75) -> bool:
        """
        Check if content is similar to recent newsletter topics

        Args:
            title: Title of the new content to check
            similarity_threshold: Threshold for similarity (0-1)

        Returns:
            True if similar content was recently covered
        """
        recent_topics = self.get_recent_topics()

        for past_title in recent_topics:
            similarity = SequenceMatcher(None, title.lower(), past_title.lower()).ratio()
            if similarity >= similarity_threshold:
                return True

        return False

    def is_duplicate_url(self, url: str) -> bool:
        """
        Check if a URL was already featured in recent newsletters

        Args:
            url: URL to check

        Returns:
            True if URL was recently featured
        """
        recent_urls = self.get_recent_urls()
        return url in recent_urls

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about newsletter history

        Returns:
            Dictionary with statistics
        """
        if not self.history:
            return {
                "total_newsletters": 0,
                "total_articles": 0,
                "date_range": None
            }

        total_articles = 0
        for entry in self.history:
            content = entry.get("content", {})
            for section in ["worldwide", "portugal", "ventures"]:
                total_articles += len(content.get(section, []))

        return {
            "total_newsletters": len(self.history),
            "total_articles": total_articles,
            "oldest_date": self.history[-1]["date"] if self.history else None,
            "newest_date": self.history[0]["date"] if self.history else None
        }

    def clear_old_history(self, keep_count: int = 52):
        """
        Clear old history keeping only the most recent entries

        Args:
            keep_count: Number of recent newsletters to keep (default: 52 weeks)
        """
        if len(self.history) > keep_count:
            self.history = self.history[:keep_count]
            self._save_history()
