"""LinkedIn scraper — public job search HTML."""
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, make_client

logger = logging.getLogger(__name__)

KEYWORDS = ["alternance cybersécurité", "alternance sécurité informatique", "alternance SOC"]
LOCATION = "France"


class LinkedInScraper(BaseScraper):
    name = "linkedin"

    async def scrape(self) -> list[dict]:
        results = []
        async with make_client() as client:
            for kw in KEYWORDS:
                results += await self._scrape_keyword(kw, client)
        if not results:
            logger.warning("[linkedin] 0 jobs returned — selectors may be stale")
        return results

    async def _scrape_keyword(self, keyword: str, client) -> list[dict]:
        html = await self.fetch(
            "https://www.linkedin.com/jobs/search/",
            params={"keywords": keyword, "location": LOCATION, "f_JT": "I", "f_TP": "1,2"},
            client=client,
        )
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for card in soup.select("div.base-card"):
            title_el = card.select_one("h3.base-search-card__title")
            company_el = card.select_one("h4.base-search-card__subtitle")
            location_el = card.select_one("span.job-search-card__location")
            link_el = card.select_one("a.base-card__full-link")
            if not title_el:
                continue
            results.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "city": location_el.get_text(strip=True) if location_el else "",
                "url": link_el["href"].split("?")[0] if link_el else "",
                "source": self.name,
                "contract_type": "Alternance",
            })
        logger.info("[linkedin] %d jobs for '%s'", len(results), keyword)
        return results


async def scrape_linkedin():
    return await LinkedInScraper().scrape()
