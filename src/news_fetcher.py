"""
News Fetcher Module
Fetches news articles from various sources including RSS feeds and web scraping
"""

import requests
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from newspaper import Article
import yaml


class NewsFetcher:
    """Fetches news articles from configured sources"""

    def __init__(self, sources_config: str = "config/sources.yaml", max_age_days: int = 7):
        """
        Initialize the news fetcher

        Args:
            sources_config: Path to sources configuration file
            max_age_days: Maximum age of articles to fetch (in days)
        """
        self.max_age_days = max_age_days
        self.sources = self._load_sources(sources_config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _load_sources(self, config_file: str) -> Dict[str, Any]:
        """Load news sources from configuration file"""
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def fetch_all_news(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Fetch news from all configured sources

        Returns:
            Dictionary with categorized news articles
        """
        all_news = {
            "worldwide": [],
            "portugal": [],
            "ventures": []
        }

        # Fetch worldwide news
        if "worldwide" in self.sources:
            print("Fetching worldwide news...")
            all_news["worldwide"] = self._fetch_from_sources(self.sources["worldwide"])

        # Fetch Portugal news
        if "portugal" in self.sources:
            print("Fetching Portugal news...")
            all_news["portugal"] = self._fetch_from_sources(self.sources["portugal"])

        # Fetch ventures-related news
        if "ventures" in self.sources:
            print("Fetching ventures news...")
            all_news["ventures"] = self._fetch_ventures_news()

        return all_news

    def _fetch_from_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fetch articles from a list of sources

        Args:
            sources: List of source configurations

        Returns:
            List of article dictionaries
        """
        articles = []

        for source in sources:
            try:
                if source.get("type") == "rss" and "rss" in source:
                    articles.extend(self._fetch_rss(source))
                elif source.get("type") == "web":
                    articles.extend(self._fetch_web(source))
            except Exception as e:
                print(f"Error fetching from {source.get('name', 'unknown')}: {e}")

        return articles

    def _fetch_rss(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch articles from RSS feed

        Args:
            source: Source configuration dictionary

        Returns:
            List of article dictionaries
        """
        articles = []
        feed = feedparser.parse(source["rss"])

        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

        for entry in feed.entries[:15]:  # Limit to 15 most recent entries
            try:
                # Parse publication date
                pub_date = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6])

                # Skip old articles
                if pub_date and pub_date < cutoff_date:
                    continue

                # Extract article content
                article_data = {
                    "title": entry.title,
                    "url": entry.link,
                    "source": source.get("name", "Unknown"),
                    "published": pub_date.isoformat() if pub_date else None,
                    "summary": entry.get("summary", ""),
                }

                # Try to get full article content
                try:
                    full_content = self._extract_article_content(entry.link)
                    if full_content:
                        article_data["content"] = full_content
                except:
                    article_data["content"] = article_data["summary"]

                articles.append(article_data)

            except Exception as e:
                print(f"Error parsing RSS entry from {source.get('name')}: {e}")
                continue

        return articles

    def _fetch_web(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch articles by scraping web pages

        Args:
            source: Source configuration dictionary

        Returns:
            List of article dictionaries
        """
        articles = []

        try:
            response = self.session.get(source["url"], timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Find article links (common patterns)
            article_links = []

            # Try common article link patterns
            for selector in ['article a', '.article-link', 'h2 a', 'h3 a', '.headline a']:
                links = soup.select(selector)
                if links:
                    article_links.extend(links)
                    break

            # Extract unique URLs
            urls_seen = set()
            for link in article_links[:10]:  # Limit to 10 articles
                href = link.get('href')
                if not href:
                    continue

                # Make absolute URL
                if href.startswith('/'):
                    from urllib.parse import urljoin
                    href = urljoin(source["url"], href)

                if href in urls_seen:
                    continue
                urls_seen.add(href)

                try:
                    article_data = self._extract_article_content(href)
                    if article_data:
                        article_data["source"] = source.get("name", "Unknown")
                        articles.append(article_data)
                except Exception as e:
                    print(f"Error extracting article from {href}: {e}")
                    continue

        except Exception as e:
            print(f"Error scraping {source.get('name')}: {e}")

        return articles

    def _extract_article_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract article content using newspaper3k

        Args:
            url: Article URL

        Returns:
            Article data dictionary or None
        """
        try:
            article = Article(url)
            article.download()
            article.parse()

            # Check if article is recent enough
            if article.publish_date:
                cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
                if article.publish_date.replace(tzinfo=None) < cutoff_date:
                    return None

            return {
                "title": article.title,
                "url": url,
                "published": article.publish_date.isoformat() if article.publish_date else None,
                "content": article.text,
                "summary": article.meta_description or article.text[:500],
                "authors": article.authors,
                "top_image": article.top_image
            }

        except Exception as e:
            print(f"Error extracting article content: {e}")
            return None

    def _fetch_ventures_news(self) -> List[Dict[str, Any]]:
        """
        Fetch news related to CFT ventures (Sofia and FIXO)

        Returns:
            List of venture-related articles
        """
        articles = []
        ventures_config = self.sources.get("ventures", {})

        keywords = ventures_config.get("keywords", [])
        sources = ventures_config.get("sources", [])

        # Fetch from ventures-specific sources
        venture_articles = self._fetch_from_sources(sources)

        # Filter articles by keywords
        for article in venture_articles:
            content_text = (
                article.get("title", "") + " " +
                article.get("summary", "") + " " +
                article.get("content", "")
            ).lower()

            # Check if any keyword is mentioned
            for keyword in keywords:
                if keyword.lower() in content_text:
                    article["matched_keyword"] = keyword
                    articles.append(article)
                    break

        return articles

    def search_by_keywords(self, keywords: List[str], section: str = "worldwide") -> List[Dict[str, Any]]:
        """
        Search for articles matching specific keywords

        Args:
            keywords: List of keywords to search for
            section: Section to search in (worldwide, portugal, ventures)

        Returns:
            List of matching articles
        """
        if section not in self.sources:
            return []

        sources = self.sources[section]
        all_articles = self._fetch_from_sources(sources)

        matching_articles = []
        for article in all_articles:
            content_text = (
                article.get("title", "") + " " +
                article.get("summary", "") + " " +
                article.get("content", "")
            ).lower()

            for keyword in keywords:
                if keyword.lower() in content_text:
                    article["matched_keyword"] = keyword
                    matching_articles.append(article)
                    break

        return matching_articles
