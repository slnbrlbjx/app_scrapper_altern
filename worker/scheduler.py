import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler

from scrapers.linkedin_scraper import scrape_linkedin

scheduler = BlockingScheduler()


async def run_scrapers():
    jobs = await scrape_linkedin()

    print(f"Collected {len(jobs)} jobs")


@scheduler.scheduled_job("interval", minutes=30)
def scheduled_scraping():
    asyncio.run(run_scrapers())


scheduler.start()