"""Indeed scraper — HTML parsing (Indeed blocks APIs, requires careful rate limiting)."""
import logging
import asyncio
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

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
        for q in QUERIES:
            items = await self._scrape_query(q)
            results += items
            await asyncio.sleep(2)  # Polite delay between queries
        return results

    async def _scrape_query(self, query: str) -> list[dict]:
        html = await self.fetch(
            BASE_URL,
            params={"q": query, "l": "France", "sc": "0kf%3Ajt%28INTERN%29%3B"},
        )
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        results = []
        # Indeed job cards (2024 structure)
        for card in soup.select("div.job_seen_beacon, li.css-5lfssm"):
            title_el = card.select_one("h2.jobTitle span[title], h2.jobTitle a span")
            company_el = card.select_one("[data-testid='company-name'], span.css-63koeb")
            location_el = card.select_one("[data-testid='text-location']")
            link_el = card.select_one("h2.jobTitle a")
            if not title_el:
                continue
            job_id = link_el["data-jk"] if link_el and link_el.get("data-jk") else ""
            results.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "city": location_el.get_text(strip=True) if location_el else "",
                "url": f"https://fr.indeed.com/viewjob?jk={job_id}" if job_id else "",
                "source": self.name,
                "contract_type": "Alternance",
            })
        logger.info(f"[indeed] {len(results)} jobs for '{query}'")
        return results


async def scrape_indeed():
    return await IndeedScraper().scrape()
