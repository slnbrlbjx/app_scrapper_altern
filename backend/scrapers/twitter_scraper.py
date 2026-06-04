"""X/Twitter scraper — Nitter public RSS feeds."""
import asyncio
import logging
import feedparser
from scrapers.base import BaseScraper, make_client

logger = logging.getLogger(__name__)

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
        async with make_client() as client:
            for term in SEARCH_TERMS:
                for instance in NITTER_INSTANCES:
                    feed_url = f"{instance}/search/rss?q={term.replace(' ', '+')}&f=tweets"
                    html = await self.fetch(feed_url, client=client)
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
                    break
                await asyncio.sleep(1)
        logger.info("[twitter] %d tweets", len(results))
        return results


async def scrape_twitter():
    return await TwitterScraper().scrape()
