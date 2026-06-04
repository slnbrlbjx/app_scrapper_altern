"""Reddit scraper — public JSON API, no auth required."""
import asyncio
import logging
from scrapers.base import BaseScraper, make_client

logger = logging.getLogger(__name__)

SEARCH_TERMS = ["alternance cybersécurité", "alternance cyber", "alternance sécurité"]


class RedditScraper(BaseScraper):
    name = "reddit"

    async def scrape(self) -> list[dict]:
        results = []
        async with make_client(json=True) as client:
            for term in SEARCH_TERMS:
                data = await self.fetch_json(
                    "https://www.reddit.com/search.json",
                    params={"q": term, "sort": "new", "t": "month", "limit": 25, "type": "link"},
                    client=client,
                )
                if data:
                    for post in data.get("data", {}).get("children", []):
                        p = post.get("data", {})
                        results.append({
                            "title": p.get("title", ""),
                            "company": f"r/{p.get('subreddit', '')}",
                            "url": f"https://reddit.com{p.get('permalink', '')}",
                            "source": self.name,
                            "description": p.get("selftext", "")[:500],
                            "contract_type": "Post",
                        })
                await asyncio.sleep(1)
        logger.info("[reddit] %d posts", len(results))
        return results


async def scrape_reddit():
    return await RedditScraper().scrape()
