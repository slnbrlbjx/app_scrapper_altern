"""X/Twitter scraper — uses Nitter public instances (no API key needed).

Nitter is a privacy-focused Twitter frontend that exposes public tweets.
We use the RSS feeds which are more stable than HTML scraping.
"""
import logging
import feedparser
import asyncio
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# Public Nitter instances (some may be down — we try multiple)
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.1d4.us",
]

SEARCH_TERMS = [
    "alternance cybersécurité",
    "alternance cyber",
    "#alternance #cybersécurité",
    "recrutement cybersécurité alternance",
]


class TwitterScraper(BaseScraper):
    name = "twitter"

    async def scrape(self) -> list[dict]:
        results = []
        for term in SEARCH_TERMS:
            for instance in NITTER_INSTANCES:
                try:
                    feed_url = f"{instance}/search/rss?q={term.replace(' ', '+')}&f=tweets"
                    html = await self.fetch(feed_url)
                    if not html:
                        continue
                    feed = feedparser.parse(html)
                    if not feed.entries:
                        continue
                    for entry in feed.entries[:20]:
                        results.append({
                            "title": entry.get("title", "")[:200],
                            "company": entry.get("author", ""),
                            "url": entry.get("link", "").replace(instance, "https://twitter.com"),
                            "source": self.name,
                            "description": entry.get("summary", "")[:500],
                            "contract_type": "Tweet",
                        })
                    break  # Success — no need to try other instances
                except Exception as e:
                    logger.debug(f"[twitter] {instance} failed: {e}")
            await asyncio.sleep(1)
        logger.info(f"[twitter] {len(results)} tweets")
        return results


async def scrape_twitter():
    return await TwitterScraper().scrape()
