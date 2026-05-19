"""
Scheduler: runs all scrapers every 30 minutes and saves results to DB.
"""
import sys
import os
import asyncio
import logging

# Ensure backend modules are on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from database.database import save_jobs
from services.filter import is_cyber_job
from services.discord import send_discord_alert

# Import all scrapers
from scrapers.linkedin_scraper import scrape_linkedin
from scrapers.wttj_scraper import scrape_wttj
from scrapers.hellowork_scraper import scrape_hellowork
from scrapers.apec_scraper import scrape_apec
from scrapers.indeed_scraper import scrape_indeed
from scrapers.lesjeudis_scraper import scrape_lesjeudis
from scrapers.francetravail_scraper import scrape_francetravail
from scrapers.reddit_scraper import scrape_reddit
from scrapers.twitter_scraper import scrape_twitter
from scrapers.linkedin_posts_scraper import scrape_linkedin_posts
from scrapers.discord_scraper import scrape_discord
from scrapers.telegram_scraper import scrape_telegram
from scrapers.companies_scraper import scrape_companies

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

SCRAPERS = [
    ("linkedin", scrape_linkedin),
    ("welcometothejungle", scrape_wttj),
    ("hellowork", scrape_hellowork),
    ("apec", scrape_apec),
    ("indeed", scrape_indeed),
    ("lesjeudis", scrape_lesjeudis),
    ("france_travail", scrape_francetravail),
    ("reddit", scrape_reddit),
    ("twitter", scrape_twitter),
    ("linkedin_posts", scrape_linkedin_posts),
    ("discord", scrape_discord),
    ("telegram", scrape_telegram),
    ("companies", scrape_companies),
]


async def run_scrapers():
    logger.info("=== Starting scrape cycle ===")
    total_new = 0

    for source_name, scraper_fn in SCRAPERS:
        try:
            logger.info(f"[{source_name}] Scraping...")
            jobs = await scraper_fn()

            # Filter to cyber-relevant jobs only
            filtered = [j for j in jobs if is_cyber_job(
                f"{j.get('title', '')} {j.get('description', '')} {j.get('company', '')}"
            )]

            logger.info(f"[{source_name}] {len(jobs)} found → {len(filtered)} relevant")

            new_count = save_jobs(filtered, source=source_name)
            total_new += new_count

            # Discord alert for new jobs
            if new_count > 0:
                for job in filtered[:new_count]:  # Alert for genuinely new ones
                    try:
                        await send_discord_alert(job)
                    except Exception as e:
                        logger.warning(f"Discord alert failed: {e}")

        except Exception as e:
            logger.error(f"[{source_name}] Scraper crashed: {e}", exc_info=True)

    logger.info(f"=== Cycle done: {total_new} new jobs saved ===")


def run():
    asyncio.run(run_scrapers())


scheduler = BlockingScheduler(timezone="Europe/Paris")
scheduler.add_job(
    run,
    trigger=IntervalTrigger(minutes=30),
    id="scrape_all",
    name="Scrape all sources",
    replace_existing=True,
)

if __name__ == "__main__":
    logger.info("Scheduler starting — first run immediately")
    run()  # Run once on startup
    scheduler.start()
