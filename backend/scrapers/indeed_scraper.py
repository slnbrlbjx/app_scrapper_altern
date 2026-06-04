"""Indeed scraper — HTML parsing with shared client and polite delays."""
import asyncio
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, make_client

logger = logging.getLogger(__name__)

BASE_URL = "https://fr.indeed.com/jobs"
QUERIES = [
    "alternance cybersécurité",
    "alternance sécurité informatique",
    "alternance SOC",
    "alternance pentest",
]


class IndeedScraper(BaseScraper):
    name = "indeed"

    async def scrape(self) -> list[dict]:
        results = []
        async with make_client() as client:
            for q in QUERIES:
                results += await self._scrape_query(q, client)
                await asyncio.sleep(2)
        if not results:
            logger.warning("[indeed] 0 jobs — selectors may be stale")
        return results

    async def _scrape_query(self, query: str, client) -> list[dict]:
        html = await self.fetch(
            BASE_URL,
            params={"q": query, "l": "France", "sc": "0kf%3Ajt%28INTERN%29%3B"},
            client=client,
        )
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for card in soup.select("div.job_seen_beacon, li.css-5lfssm"):
            title_el = card.select_one("h2.jobTitle span[title], h2.jobTitle a span")
            company_el = card.select_one("[data-testid='company-name'], span.css-63koeb")
            location_el = card.select_one("[data-testid='text-location']")
            link_el = card.select_one("h2.jobTitle a")
            if not title_el:
                continue
            job_id = link_el.get("data-jk", "") if link_el else ""
            results.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "city": location_el.get_text(strip=True) if location_el else "",
                "url": f"https://fr.indeed.com/viewjob?jk={job_id}" if job_id else "",
                "source": self.name,
                "contract_type": "Alternance",
            })
        logger.info("[indeed] %d jobs for '%s'", len(results), query)
        return results


async def scrape_indeed():
    return await IndeedScraper().scrape()
