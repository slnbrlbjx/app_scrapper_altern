"""Hellowork scraper — public HTML."""
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.hellowork.com/fr-fr/emploi/recherche.html"
KEYWORDS = [
    ("alternance", "cybersécurité"),
    ("alternance", "sécurité informatique"),
    ("alternance", "SOC analyste"),
]


class HelloworkScraper(BaseScraper):
    name = "hellowork"

    async def scrape(self) -> list[dict]:
        results = []
        for contract, kw in KEYWORDS:
            html = await self.fetch(
                BASE_URL,
                params={"k": f"{contract} {kw}", "c": "Alternance"},
            )
            if not html:
                continue
            soup = BeautifulSoup(html, "html.parser")
            for card in soup.select("li[data-id]"):
                title_el = card.select_one("h2, h3, [class*='title']")
                company_el = card.select_one("[class*='company'], [class*='entreprise']")
                city_el = card.select_one("[class*='city'], [class*='location']")
                link_el = card.select_one("a[href]")
                if not title_el:
                    continue
                href = link_el["href"] if link_el else ""
                results.append({
                    "title": title_el.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "city": city_el.get_text(strip=True) if city_el else "",
                    "url": f"https://www.hellowork.com{href}" if href.startswith("/") else href,
                    "source": self.name,
                    "contract_type": "Alternance",
                })
        logger.info(f"[hellowork] {len(results)} total jobs")
        return results


async def scrape_hellowork():
    return await HelloworkScraper().scrape()
