"""
Scheduler: runs all scrapers every 30 minutes.
Entrypoint: python -m worker.scheduler  (from /app)
"""
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from database.database import save_jobs
from services.discord import send_discord_alert
from services.filter import is_cyber_job
from scrapers.apec_scraper import scrape_apec
from scrapers.companies_scraper import scrape_companies
from scrapers.discord_scraper import scrape_discord
from scrapers.francetravail_scraper import scrape_francetravail
from scrapers.hellowork_scraper import scrape_hellowork
from scrapers.indeed_scraper import scrape_indeed
from scrapers.lesjeudis_scraper import scrape_lesjeudis
from scrapers.linkedin_posts_scraper import scrape_linkedin_posts
from scrapers.linkedin_scraper import scrape_linkedin
from scrapers.reddit_scraper import scrape_reddit
from scrapers.telegram_scraper import scrape_telegram
from scrapers.twitter_scraper import scrape_twitter
from scrapers.wttj_scraper import scrape_wttj

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
    logger.info("=== scrape cycle start ===")
    total_new = 0

    for source_name, scraper_fn in SCRAPERS:
        try:
            jobs = await scraper_fn()
            filtered = [
                j for j in jobs
                if is_cyber_job(f"{j.get('title', '')} {j.get('description', '')} {j.get('company', '')}")
            ]
            logger.info("[%s] %d found → %d relevant", source_name, len(jobs), len(filtered))

            # save_jobs returns only the dicts that were actually inserted
            new_jobs = save_jobs(filtered, source=source_name)
            total_new += len(new_jobs)

            # Alert on the real new ones, cap at 5 per source to avoid webhook spam
            for job in new_jobs[:5]:
                try:
                    await send_discord_alert(job)
                except Exception as e:
                    logger.warning("Discord alert failed: %s", e)

        except Exception as e:
            logger.error("[%s] crashed: %s", source_name, e, exc_info=True)

    logger.info("=== cycle done: %d new jobs ===", total_new)


async def main():
    scheduler = AsyncIOScheduler(timezone="Europe/Paris")
    scheduler.add_job(
        run_scrapers,
        trigger=IntervalTrigger(minutes=30),
        id="scrape_all",
        replace_existing=True,
    )
    logger.info("scheduler starting — running once immediately")
    await run_scrapers()
    scheduler.start()
    # Keep the event loop alive
    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
