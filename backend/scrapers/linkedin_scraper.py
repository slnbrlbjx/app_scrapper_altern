"""LinkedIn scraper — uses public job search RSS + HTML fallback."""
import logging
import feedparser
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

KEYWORDS = ["alternance cybersécurité", "alternance sécurité informatique", "alternance SOC"]
LOCATION = "France"


class LinkedInScraper(BaseScraper):
    name = "linkedin"

    async def scrape(self) -> list[dict]:
        jobs = []
        for kw in KEYWORDS:
            jobs += await self._scrape_keyword(kw)
        return jobs

    async def _scrape_keyword(self, keyword: str) -> list[dict]:
        """LinkedIn public job search — HTML parsing (no auth needed)."""
        results = []
        url = "https://www.linkedin.com/jobs/search/"
        params = {
            "keywords": keyword,
            "location": LOCATION,
            "f_JT": "I",  # Internship/alternance
            "f_TP": "1,2",
        }
        html = await self.fetch(url, params=params)
        if not html:
            return results

        soup = BeautifulSoup(html, "html.parser")
        # LinkedIn public page card selectors (2024+)
        cards = soup.select("div.base-card")
        for card in cards:
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
        logger.info(f"[linkedin] {len(results)} jobs for '{keyword}'")
        return results


async def scrape_linkedin():
    return await LinkedInScraper().scrape()
