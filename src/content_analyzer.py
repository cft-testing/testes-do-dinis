"""
Content Analyzer Module
Uses AI to analyze and score content relevance for Fidelidade CFT
"""

import os
from typing import Dict, Any, List, Optional
import yaml
import json
from anthropic import Anthropic
from openai import OpenAI


class ContentAnalyzer:
    """Analyzes content relevance using AI"""

    def __init__(
        self,
        settings_config: str = "config/settings.yaml",
        topics_config: str = "config/topics.yaml"
    ):
        """
        Initialize the content analyzer

        Args:
            settings_config: Path to settings configuration
            topics_config: Path to topics configuration
        """
        with open(settings_config, 'r', encoding='utf-8') as f:
            self.settings = yaml.safe_load(f)

        with open(topics_config, 'r', encoding='utf-8') as f:
            self.topics = yaml.safe_load(f)

        # Initialize AI client
        ai_config = self.settings.get("ai", {})
        self.provider = ai_config.get("provider", "anthropic")

        if self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set in environment")
            self.client = Anthropic(api_key=api_key)
            self.model = ai_config.get("model", "claude-3-5-sonnet-20241022")
        elif self.provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set in environment")
            self.client = OpenAI(api_key=api_key)
            self.model = ai_config.get("model", "gpt-4-turbo-preview")
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

        self.temperature = ai_config.get("temperature", 0.3)
        self.max_tokens = ai_config.get("max_tokens", 4000)

    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze an article and score its relevance

        Args:
            article: Article dictionary with title, content, etc.

        Returns:
            Analysis results with scores and recommendations
        """
        # Prepare analysis prompt
        prompt = self._create_analysis_prompt(article)

        # Call AI
        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{"role": "user", "content": prompt}]
                )
                analysis_text = response.content[0].text
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                analysis_text = response.choices[0].message.content

            # Parse the JSON response
            analysis = json.loads(analysis_text)

            # Calculate overall score
            analysis["overall_score"] = self._calculate_overall_score(analysis)

            return analysis

        except Exception as e:
            print(f"Error analyzing article: {e}")
            return self._default_analysis()

    def _create_analysis_prompt(self, article: Dict[str, Any]) -> str:
        """Create the analysis prompt for the AI"""

        topics_list = "\n".join([
            f"- {t['name']}: {', '.join(t['keywords'][:5])}"
            for t in self.topics.get("topics", [])
        ])

        prompt = f"""You are a technology and business analyst for Fidelidade, a leading Portuguese insurance company. Your task is to analyze the following news article and evaluate its relevance for the Center for Transformation (CFT) team.

**Article Information:**
Title: {article.get('title', 'N/A')}
Source: {article.get('source', 'N/A')}
URL: {article.get('url', 'N/A')}
Date: {article.get('published', 'N/A')}

**Content:**
{article.get('content', article.get('summary', 'N/A'))[:3000]}

**Context about Fidelidade and CFT:**
- Fidelidade is Portugal's largest insurance company
- CFT (Center for Transformation) drives digital innovation and transformation
- Current ventures: Sofia (AI virtual assistant) and FIXO (home services platform)
- Focus areas: InsurTech, AI/ML, customer experience, digital transformation

**Predefined Topics of Interest:**
{topics_list}

**Your Task:**
Analyze this article and provide scores (0-10) for each criterion below. Be critical and realistic - not every article deserves high scores.

Return ONLY a valid JSON object with this exact structure (no markdown, no explanations):
{{
  "business_relevance": <score 0-10>,
  "business_relevance_reasoning": "<brief explanation>",
  "disruptive_potential": <score 0-10>,
  "disruptive_potential_reasoning": "<brief explanation>",
  "internal_know_how": <score 0-10>,
  "internal_know_how_reasoning": "<brief explanation>",
  "market_potential": <score 0-10>,
  "market_potential_reasoning": "<brief explanation>",
  "need_for_action": <score 0-10>,
  "need_for_action_reasoning": "<brief explanation>",
  "strategic_fit": <score 0-10>,
  "strategic_fit_reasoning": "<brief explanation>",
  "time_to_market_impact": <score 0-10>,
  "time_to_market_impact_reasoning": "<brief explanation>",
  "trend_maturity": <score 0-10>,
  "trend_maturity_reasoning": "<brief explanation>",
  "recommended_action": "<MONITOR|EXPLORE|PILOT|IMPLEMENT|IGNORE>",
  "key_insights": ["<insight 1>", "<insight 2>", "<insight 3>"],
  "related_topics": ["<topic 1>", "<topic 2>"],
  "summary": "<2-3 sentence summary of why this matters to CFT>"
}}

**Scoring Guidelines:**
- Business Relevance: How relevant is this to Fidelidade's insurance business?
- Disruptive Potential: Could this disrupt the insurance/financial services industry?
- Internal Know-How: Do we have expertise in this area?
- Market Potential: Market size and opportunity
- Need for Action: Urgency - do we need to act on this soon?
- Strategic Fit: Alignment with CFT and Fidelidade strategy
- Time to Market Impact: How quickly could this be implemented/adopted?
- Trend Maturity: Is this emerging (0-3), growing (4-7), or mature (8-10)?

**Recommended Actions:**
- IGNORE: Not relevant
- MONITOR: Track developments
- EXPLORE: Research further
- PILOT: Test/prototype
- IMPLEMENT: Take action now"""

        return prompt

    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate weighted overall score"""
        weights = self.settings.get("relevance", {}).get("weights", {})

        score = 0.0
        score += analysis.get("business_relevance", 0) * weights.get("business_relevance", 0.2)
        score += analysis.get("disruptive_potential", 0) * weights.get("disruptive_potential", 0.15)
        score += analysis.get("internal_know_how", 0) * weights.get("internal_know_how", 0.1)
        score += analysis.get("market_potential", 0) * weights.get("market_potential", 0.15)
        score += analysis.get("need_for_action", 0) * weights.get("need_for_action", 0.1)
        score += analysis.get("strategic_fit", 0) * weights.get("strategic_fit", 0.15)
        score += analysis.get("time_to_market_impact", 0) * weights.get("time_to_market_impact", 0.1)
        score += analysis.get("trend_maturity", 0) * weights.get("trend_maturity", 0.05)

        return round(score, 2)

    def _default_analysis(self) -> Dict[str, Any]:
        """Return default analysis on error"""
        return {
            "business_relevance": 5,
            "disruptive_potential": 5,
            "internal_know_how": 5,
            "market_potential": 5,
            "need_for_action": 5,
            "strategic_fit": 5,
            "time_to_market_impact": 5,
            "trend_maturity": 5,
            "overall_score": 5.0,
            "recommended_action": "MONITOR",
            "key_insights": [],
            "related_topics": [],
            "summary": "Analysis unavailable"
        }

    def filter_by_relevance(
        self,
        articles: List[Dict[str, Any]],
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze and filter articles by relevance score

        Args:
            articles: List of articles to analyze
            min_score: Minimum relevance score (uses config default if not provided)

        Returns:
            List of articles with analysis, sorted by score
        """
        if min_score is None:
            min_score = self.settings.get("relevance", {}).get("min_score", 6.0)

        analyzed_articles = []

        for article in articles:
            print(f"Analyzing: {article.get('title', 'Unknown')[:60]}...")

            analysis = self.analyze_article(article)

            if analysis["overall_score"] >= min_score:
                article["analysis"] = analysis
                analyzed_articles.append(article)

        # Sort by score (highest first)
        analyzed_articles.sort(
            key=lambda x: x["analysis"]["overall_score"],
            reverse=True
        )

        return analyzed_articles

    def batch_analyze(
        self,
        articles_by_section: Dict[str, List[Dict[str, Any]]],
        min_score: Optional[float] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze articles for all sections

        Args:
            articles_by_section: Dictionary with section names as keys
            min_score: Minimum relevance score

        Returns:
            Dictionary with analyzed and filtered articles by section
        """
        results = {}

        for section, articles in articles_by_section.items():
            print(f"\n=== Analyzing {section} section ({len(articles)} articles) ===")
            results[section] = self.filter_by_relevance(articles, min_score)
            print(f"Selected {len(results[section])} relevant articles for {section}")

        return results
