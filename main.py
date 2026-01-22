#!/usr/bin/env python3
"""
CFT Trend Radar Newsletter - Main Orchestration Script
Automated weekly newsletter generation for Center for Transformation - Fidelidade
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from news_fetcher import NewsFetcher
from content_analyzer import ContentAnalyzer
from context_manager import ContextManager
from newsletter_generator import NewsletterGenerator
from email_sender import EmailSender
from scheduler import NewsletterScheduler


class TrendRadarNewsletter:
    """Main orchestration class for Trend Radar Newsletter"""

    def __init__(self):
        """Initialize all components"""
        print("Initializing CFT Trend Radar Newsletter System...")

        self.fetcher = NewsFetcher()
        self.analyzer = ContentAnalyzer()
        self.context = ContextManager()
        self.generator = NewsletterGenerator()
        self.email = EmailSender()
        self.scheduler = NewsletterScheduler()

        print("System initialized successfully!")

    def generate_newsletter(self) -> dict:
        """
        Generate a complete newsletter

        Returns:
            Newsletter data dictionary
        """
        print("\n" + "="*80)
        print("GENERATING CFT TREND RADAR NEWSLETTER")
        print("="*80)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Step 1: Fetch news
        print("\n[1/5] Fetching news from sources...")
        all_news = self.fetcher.fetch_all_news()

        print(f"   - Worldwide: {len(all_news.get('worldwide', []))} articles")
        print(f"   - Portugal: {len(all_news.get('portugal', []))} articles")
        print(f"   - Ventures: {len(all_news.get('ventures', []))} articles")

        # Step 2: Filter by context (remove duplicates)
        print("\n[2/5] Filtering out duplicate content...")
        filtered_news = {}
        for section, articles in all_news.items():
            filtered_articles = []
            for article in articles:
                # Check for duplicate URL
                if self.context.is_duplicate_url(article.get('url', '')):
                    continue

                # Check for similar content
                if self.context.is_similar_content(article.get('title', '')):
                    continue

                filtered_articles.append(article)

            filtered_news[section] = filtered_articles
            print(f"   - {section}: {len(filtered_articles)} unique articles")

        # Step 3: Analyze content
        print("\n[3/5] Analyzing content relevance...")
        analyzed_news = self.analyzer.batch_analyze(filtered_news)

        total_selected = sum(len(articles) for articles in analyzed_news.values())
        print(f"   - Total relevant articles: {total_selected}")

        # Check if we have enough content
        if total_selected == 0:
            print("\n⚠️  No relevant content found for this week.")
            print("Newsletter generation skipped.")
            return None

        # Step 4: Generate newsletter
        print("\n[4/5] Generating newsletter...")
        newsletter = self.generator.generate(analyzed_news)

        print(f"   - Sections: {newsletter['sections_count']}")
        print(f"   - Total articles: {newsletter['total_articles']}")

        # Step 5: Save to context
        print("\n[5/5] Saving to history...")
        self.context.add_newsletter(newsletter['content'])

        print("\n✓ Newsletter generated successfully!")

        return newsletter

    def send_newsletter(self, newsletter: dict = None) -> bool:
        """
        Send newsletter via email

        Args:
            newsletter: Newsletter data (generates new one if not provided)

        Returns:
            True if sent successfully
        """
        if newsletter is None:
            newsletter = self.generate_newsletter()

        if newsletter is None:
            return False

        print("\nSending newsletter via email...")

        success = self.email.send_newsletter(
            html_content=newsletter['html'],
            text_content=newsletter['text']
        )

        return success

    def run_scheduled(self):
        """Run newsletter generation and sending on schedule"""
        def job():
            """Scheduled job function"""
            try:
                print("\n" + "="*80)
                print("SCHEDULED NEWSLETTER GENERATION")
                print("="*80)

                success = self.send_newsletter()

                if success:
                    print("\n✓ Scheduled newsletter completed successfully!")
                else:
                    print("\n✗ Scheduled newsletter failed.")

            except Exception as e:
                print(f"\n✗ Error in scheduled job: {e}")

        # Schedule the job
        self.scheduler.schedule_weekly(job)

        # Show next run time
        next_run = self.scheduler.get_next_run()
        if next_run:
            print(f"\nNext newsletter scheduled for: {next_run}")

        # Run continuously
        self.scheduler.run_continuously()

    def preview_newsletter(self, output_file: str = "preview.html"):
        """
        Generate and save newsletter preview to HTML file

        Args:
            output_file: Path to save HTML preview
        """
        newsletter = self.generate_newsletter()

        if newsletter is None:
            return

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(newsletter['html'])

        print(f"\n✓ Preview saved to: {output_file}")
        print(f"Open this file in your browser to view the newsletter.")

    def show_statistics(self):
        """Show newsletter statistics"""
        stats = self.context.get_statistics()

        print("\n" + "="*80)
        print("CFT TREND RADAR NEWSLETTER - STATISTICS")
        print("="*80)
        print(f"Total newsletters sent: {stats['total_newsletters']}")
        print(f"Total articles featured: {stats['total_articles']}")

        if stats['oldest_date']:
            print(f"First newsletter: {stats['oldest_date'][:10]}")
        if stats['newest_date']:
            print(f"Latest newsletter: {stats['newest_date'][:10]}")

        print("="*80)


def main():
    """Main entry point"""

    # Load environment variables
    load_dotenv()

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="CFT Trend Radar Newsletter - Automated weekly newsletter generator"
    )

    parser.add_argument(
        "command",
        choices=["generate", "send", "schedule", "preview", "stats", "test-email"],
        help="Command to execute"
    )

    parser.add_argument(
        "--output",
        "-o",
        default="preview.html",
        help="Output file for preview (default: preview.html)"
    )

    parser.add_argument(
        "--test-recipient",
        "-t",
        help="Email address for test email"
    )

    args = parser.parse_args()

    try:
        # Create newsletter system
        newsletter_system = TrendRadarNewsletter()

        # Execute command
        if args.command == "generate":
            newsletter_system.generate_newsletter()

        elif args.command == "send":
            newsletter_system.send_newsletter()

        elif args.command == "schedule":
            newsletter_system.run_scheduled()

        elif args.command == "preview":
            newsletter_system.preview_newsletter(args.output)

        elif args.command == "stats":
            newsletter_system.show_statistics()

        elif args.command == "test-email":
            if not args.test_recipient:
                print("Error: --test-recipient required for test-email command")
                sys.exit(1)

            print(f"Sending test email to {args.test_recipient}...")
            success = newsletter_system.email.send_test_email(args.test_recipient)

            if success:
                print("✓ Test email sent successfully!")
            else:
                print("✗ Failed to send test email")
                sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
