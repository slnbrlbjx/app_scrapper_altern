"""Welcome to the Jungle scraper — public API with HTML fallback."""
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, make_client

logger = logging.getLogger(__name__)

KEYWORDS = ["alternance cybersécurité", "alternance sécurité", "alternance SOC"]


class WTTJScraper(BaseScraper):
    name = "welcometothejungle"

    async def scrape(self) -> list[dict]:
        results = []
        async with make_client(json=True) as api_client, make_client() as html_client:
            for kw in KEYWORDS:
                data = await self.fetch_json(
                    "https://api.welcometothejungle.com/api/v1/organizations/search/jobs",
                    params={"query": kw, "contract_type[]": "alternance", "page": 1, "per_page": 50},
                    client=api_client,
                )
                if data:
                    for job in data.get("jobs", []):
                        results.append(self._parse(job))
                else:
                    results += await self._scrape_html(kw, html_client)
        if not results:
            logger.warning("[wttj] 0 jobs returned")
        return results

    async def _scrape_html(self, keyword: str, client) -> list[dict]:
        url = f"https://www.welcometothejungle.com/fr/jobs?query={keyword}&contract_type%5B%5D=ALTERNATION"
        html = await self.fetch(url, client=client)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        results = []
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
        logger.info("[wttj] %d jobs (HTML) for '%s'", len(results), keyword)
        return results

    def _parse(self, job: dict) -> dict:
        org = job.get("organization", {})
        return {
            "title": job.get("name", ""),
            "company": org.get("name", ""),
            "city": job.get("office", {}).get("city", ""),
            "url": f"https://www.welcometothejungle.com/fr/companies/{org.get('slug', '')}/jobs/{job.get('slug', '')}",
            "source": self.name,
            "contract_type": "Alternance",
            "description": job.get("description", ""),
        }


async def scrape_wttj():
    return await WTTJScraper().scrape()
