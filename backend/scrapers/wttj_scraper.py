"""Welcome to the Jungle scraper — public API."""
import logging
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

API_URL = "https://www.welcometothejungle.com/api/v1/jobs"
KEYWORDS = ["alternance cybersécurité", "alternance sécurité", "alternance SOC"]


class WTTJScraper(BaseScraper):
    name = "welcometothejungle"

    async def scrape(self) -> list[dict]:
        results = []
        for kw in KEYWORDS:
            data = await self.fetch_json(
                "https://api.welcometothejungle.com/api/v1/organizations/search/jobs",
                params={
                    "query": kw,
                    "contract_type[]": "alternance",
                    "page": 1,
                    "per_page": 50,
                },
            )
            if not data:
                # Fallback: scrape HTML search page
                results += await self._scrape_html(kw)
                continue
            for job in data.get("jobs", []):
                results.append(self._parse(job))
        return results

    async def _scrape_html(self, keyword: str) -> list[dict]:
        from bs4 import BeautifulSoup
        url = f"https://www.welcometothejungle.com/fr/jobs?query={keyword}&contract_type%5B%5D=ALTERNATION"
        html = await self.fetch(url)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        results = []
        # WTTJ server-side rendered cards
        for card in soup.select("[data-role='jobs:thumb']"):
            title_el = card.select_one("h2, h3")
            company_el = card.select_one("[data-role='company-name']")
            link_el = card.select_one("a[href*='/jobs/']")
            if not title_el:
                continue
            href = link_el["href"] if link_el else ""
            results.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "url": f"https://www.welcometothejungle.com{href}" if href.startswith("/") else href,
                "source": self.name,
                "contract_type": "Alternance",
            })
        logger.info(f"[wttj] {len(results)} jobs (HTML) for '{keyword}'")
        return results

    def _parse(self, job: dict) -> dict:
        return {
            "title": job.get("name", ""),
            "company": job.get("organization", {}).get("name", ""),
            "city": job.get("office", {}).get("city", ""),
            "url": f"https://www.welcometothejungle.com/fr/companies/{job.get('organization', {}).get('slug', '')}/jobs/{job.get('slug', '')}",
            "source": self.name,
            "contract_type": "Alternance",
            "description": job.get("description", ""),
        }


async def scrape_wttj():
    return await WTTJScraper().scrape()
