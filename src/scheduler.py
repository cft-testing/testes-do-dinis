"""
Scheduler Module
Handles automated weekly scheduling of newsletter generation
"""

import schedule
import time
import yaml
from datetime import datetime
from typing import Callable, Optional
import pytz


class NewsletterScheduler:
    """Manages automated scheduling of newsletter generation"""

    def __init__(self, settings_config: str = "config/settings.yaml"):
        """
        Initialize the scheduler

        Args:
            settings_config: Path to settings configuration
        """
        with open(settings_config, 'r', encoding='utf-8') as f:
            settings = yaml.safe_load(f)

        schedule_config = settings.get("schedule", {})

        self.day = schedule_config.get("day", "monday").lower()
        self.time = schedule_config.get("time", "09:00")
        self.timezone = schedule_config.get("timezone", "Europe/Lisbon")

        try:
            self.tz = pytz.timezone(self.timezone)
        except:
            print(f"Warning: Invalid timezone {self.timezone}, using UTC")
            self.tz = pytz.UTC

    def schedule_weekly(self, job_func: Callable) -> None:
        """
        Schedule a job to run weekly

        Args:
            job_func: Function to call when scheduled time arrives
        """
        # Map day names to schedule methods
        day_map = {
            "monday": schedule.every().monday,
            "tuesday": schedule.every().tuesday,
            "wednesday": schedule.every().wednesday,
            "thursday": schedule.every().thursday,
            "friday": schedule.every().friday,
            "saturday": schedule.every().saturday,
            "sunday": schedule.every().sunday
        }

        scheduler = day_map.get(self.day, schedule.every().monday)
        scheduler.at(self.time).do(job_func)

        print(f"Newsletter scheduled for every {self.day.capitalize()} at {self.time} ({self.timezone})")

    def run_pending(self):
        """Run any pending scheduled jobs"""
        schedule.run_pending()

    def run_continuously(self, interval: int = 60):
        """
        Run the scheduler continuously

        Args:
            interval: Seconds to wait between checks (default: 60)
        """
        print("Scheduler started. Press Ctrl+C to stop.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nScheduler stopped.")

    def get_next_run(self) -> Optional[datetime]:
        """
        Get the next scheduled run time

        Returns:
            DateTime of next run, or None if nothing scheduled
        """
        jobs = schedule.get_jobs()
        if not jobs:
            return None

        return jobs[0].next_run

    def clear_schedule(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        print("All scheduled jobs cleared")

    def run_once_now(self, job_func: Callable):
        """
        Run the job immediately (for testing)

        Args:
            job_func: Function to execute
        """
        print(f"Running job immediately at {datetime.now()}")
        job_func()
