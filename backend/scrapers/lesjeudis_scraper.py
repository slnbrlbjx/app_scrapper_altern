"""LesJeudis scraper — IT/tech job board."""
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

BASE_URL = "https://www.lesjeudis.com/offres-emploi"


class LesJeudisScraper(BaseScraper):
    name = "lesjeudis"

    async def scrape(self) -> list[dict]:
        results = []
        for page in range(1, 4):
            html = await self.fetch(
                BASE_URL,
                params={
                    "q": "cybersécurité alternance",
                    "contrat": "alternance",
                    "page": page,
                },
            )
            if not html:
                break
            soup = BeautifulSoup(html, "html.parser")
            cards = soup.select(".job-item, [class*='offer'], article.job")
            if not cards:
                break
            for card in cards:
                title_el = card.select_one("h2, h3, .job-title, [class*='title']")
                company_el = card.select_one(".company, [class*='company'], [class*='entreprise']")
                city_el = card.select_one(".location, [class*='city'], [class*='location']")
                link_el = card.select_one("a[href]")
                if not title_el:
                    continue
                href = link_el["href"] if link_el else ""
                results.append({
                    "title": title_el.get_text(strip=True),
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "city": city_el.get_text(strip=True) if city_el else "",
                    "url": f"https://www.lesjeudis.com{href}" if href.startswith("/") else href,
                    "source": self.name,
                    "contract_type": "Alternance",
                })
        logger.info(f"[lesjeudis] {len(results)} jobs")
        return results


async def scrape_lesjeudis():
    return await LesJeudisScraper().scrape()
