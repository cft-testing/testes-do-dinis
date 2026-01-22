"""
Newsletter Generator Module
Generates HTML newsletter from analyzed content
"""

from typing import Dict, Any, List
from datetime import datetime
import yaml
from jinja2 import Template


class NewsletterGenerator:
    """Generates formatted newsletter from analyzed content"""

    def __init__(self, settings_config: str = "config/settings.yaml"):
        """
        Initialize the newsletter generator

        Args:
            settings_config: Path to settings configuration
        """
        with open(settings_config, 'r', encoding='utf-8') as f:
            self.settings = yaml.safe_load(f)

        self.newsletter_config = self.settings.get("newsletter", {})

    def generate(
        self,
        content_by_section: Dict[str, List[Dict[str, Any]]],
        date: datetime = None
    ) -> Dict[str, Any]:
        """
        Generate newsletter from content

        Args:
            content_by_section: Dictionary with analyzed articles by section
            date: Newsletter date (defaults to now)

        Returns:
            Dictionary with newsletter data and HTML
        """
        if date is None:
            date = datetime.now()

        # Get week date range
        week_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = date

        # Filter and limit content per section
        newsletter_content = {}
        for section_config in self.newsletter_config.get("sections", []):
            section_id = section_config["id"]
            max_items = section_config.get("max_items", 5)
            min_items = section_config.get("min_items", 1)

            section_articles = content_by_section.get(section_id, [])

            # Only include section if it meets minimum items
            if len(section_articles) >= min_items:
                newsletter_content[section_id] = {
                    "title": section_config["title"],
                    "description": section_config.get("description", ""),
                    "articles": section_articles[:max_items]
                }

        # Generate HTML
        html = self._generate_html(newsletter_content, date)

        # Generate text version
        text = self._generate_text(newsletter_content, date)

        return {
            "date": date.isoformat(),
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "content": newsletter_content,
            "html": html,
            "text": text,
            "sections_count": len(newsletter_content),
            "total_articles": sum(len(s["articles"]) for s in newsletter_content.values())
        }

    def _generate_html(self, content: Dict[str, Any], date: datetime) -> str:
        """Generate HTML newsletter"""

        template_str = """
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ newsletter_name }} - {{ date_str }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0 0 10px 0;
            font-size: 32px;
        }
        .header p {
            margin: 0;
            opacity: 0.9;
            font-size: 16px;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 40px;
        }
        .section-header {
            font-size: 24px;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            color: #667eea;
        }
        .section-description {
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
            font-style: italic;
        }
        .article {
            background-color: #f9f9f9;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .article-title {
            font-size: 20px;
            margin: 0 0 10px 0;
            color: #333;
        }
        .article-title a {
            color: #667eea;
            text-decoration: none;
        }
        .article-title a:hover {
            text-decoration: underline;
        }
        .article-meta {
            font-size: 13px;
            color: #999;
            margin-bottom: 10px;
        }
        .article-summary {
            margin: 15px 0;
            color: #555;
        }
        .article-insights {
            background-color: #fff;
            padding: 15px;
            border-radius: 4px;
            margin-top: 15px;
        }
        .insights-title {
            font-weight: bold;
            margin-bottom: 8px;
            color: #667eea;
            font-size: 14px;
        }
        .insight-item {
            padding: 5px 0;
            font-size: 14px;
            color: #555;
        }
        .insight-item:before {
            content: "• ";
            color: #667eea;
            font-weight: bold;
        }
        .scores {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 15px;
        }
        .score-badge {
            background-color: #e8eaf6;
            color: #667eea;
            padding: 5px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .score-high {
            background-color: #c8e6c9;
            color: #2e7d32;
        }
        .score-medium {
            background-color: #fff9c4;
            color: #f57f17;
        }
        .action-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: bold;
            margin-top: 10px;
        }
        .action-monitor { background-color: #e3f2fd; color: #1976d2; }
        .action-explore { background-color: #f3e5f5; color: #7b1fa2; }
        .action-pilot { background-color: #fff3e0; color: #e65100; }
        .action-implement { background-color: #c8e6c9; color: #2e7d32; }
        .footer {
            background-color: #f5f5f5;
            padding: 20px 30px;
            text-align: center;
            color: #666;
            font-size: 13px;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ newsletter_name }}</h1>
            <p>{{ subtitle }}</p>
            <p>{{ date_str }}</p>
        </div>

        <div class="content">
            {% for section_id, section in sections.items() %}
            <div class="section">
                <h2 class="section-header">{{ section.title }}</h2>
                {% if section.description %}
                <p class="section-description">{{ section.description }}</p>
                {% endif %}

                {% for article in section.articles %}
                <div class="article">
                    <h3 class="article-title">
                        <a href="{{ article.url }}" target="_blank">{{ article.title }}</a>
                    </h3>

                    <div class="article-meta">
                        <strong>{{ article.source }}</strong>
                        {% if article.published %} • {{ article.published[:10] }}{% endif %}
                    </div>

                    <div class="article-summary">
                        {{ article.analysis.summary }}
                    </div>

                    {% if article.analysis.key_insights %}
                    <div class="article-insights">
                        <div class="insights-title">🔍 Insights Principais:</div>
                        {% for insight in article.analysis.key_insights %}
                        <div class="insight-item">{{ insight }}</div>
                        {% endfor %}
                    </div>
                    {% endif %}

                    <div class="scores">
                        <span class="score-badge {% if article.analysis.overall_score >= 8 %}score-high{% elif article.analysis.overall_score >= 6 %}score-medium{% endif %}">
                            Score: {{ article.analysis.overall_score }}/10
                        </span>
                        {% if article.analysis.related_topics %}
                        {% for topic in article.analysis.related_topics[:3] %}
                        <span class="score-badge">{{ topic }}</span>
                        {% endfor %}
                        {% endif %}
                    </div>

                    <div class="action-badge action-{{ article.analysis.recommended_action.lower() }}">
                        📋 Ação Recomendada: {{ article.analysis.recommended_action }}
                    </div>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        </div>

        <div class="footer">
            <p><strong>{{ organization }}</strong></p>
            <p>Este é um relatório automatizado gerado pelo sistema CFT Trend Radar.</p>
            <p>Para questões ou sugestões, contacte a equipa CFT.</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(template_str)

        html = template.render(
            newsletter_name=self.newsletter_config.get("name", "CFT Trend Radar"),
            subtitle=self.newsletter_config.get("subtitle", ""),
            date_str=date.strftime("%d de %B de %Y"),
            sections=content,
            organization=self.settings.get("newsletter", {}).get("organization_name", "CFT - Fidelidade")
        )

        return html

    def _generate_text(self, content: Dict[str, Any], date: datetime) -> str:
        """Generate plain text version of newsletter"""

        lines = []
        lines.append("=" * 80)
        lines.append(self.newsletter_config.get("name", "CFT Trend Radar").center(80))
        lines.append(self.newsletter_config.get("subtitle", "").center(80))
        lines.append(date.strftime("%d de %B de %Y").center(80))
        lines.append("=" * 80)
        lines.append("")

        for section_id, section in content.items():
            lines.append("")
            lines.append(section["title"])
            lines.append("-" * len(section["title"]))
            if section.get("description"):
                lines.append(section["description"])
            lines.append("")

            for i, article in enumerate(section["articles"], 1):
                lines.append(f"{i}. {article['title']}")
                lines.append(f"   Fonte: {article['source']}")
                lines.append(f"   URL: {article['url']}")
                lines.append(f"   Score: {article['analysis']['overall_score']}/10")
                lines.append(f"   Ação: {article['analysis']['recommended_action']}")
                lines.append("")
                lines.append(f"   {article['analysis']['summary']}")
                lines.append("")

                if article['analysis'].get('key_insights'):
                    lines.append("   Insights:")
                    for insight in article['analysis']['key_insights']:
                        lines.append(f"   • {insight}")
                    lines.append("")

        lines.append("=" * 80)
        lines.append("CFT - Center for Transformation - Fidelidade")
        lines.append("=" * 80)

        return "\n".join(lines)
