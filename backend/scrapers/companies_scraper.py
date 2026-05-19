"""Cyber companies career pages scraper.

Scrapes the careers/jobs pages of major French cybersecurity companies.
Each company has its own careers URL and HTML structure.
"""
import logging
import asyncio
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# Map of company -> (careers URL, CSS selectors for job cards, title, link)
COMPANIES = {
    "Advens": {
        "url": "https://www.advens.fr/carrieres",
        "card": ".job-offer, [class*='job'], article",
        "title": "h2, h3, [class*='title']",
        "link": "a[href]",
    },
    "OVHcloud": {
        "url": "https://www.ovhcloud.com/fr/company/careers/",
        "api": "https://api.ovhcloud.com/v1/recruitment/jobs?lang=fr&contractType=Apprenticeship",
        "card": ".job-card, [class*='job'], li[class*='offer']",
        "title": "h2, h3, [class*='title'], [class*='name']",
        "link": "a[href]",
    },
    "Orange Cyberdefense": {
        "url": "https://www.orangecyberdefense.com/fr/carrieres/nos-offres/",
        "card": ".job, .offer, article, [class*='card']",
        "title": "h2, h3, .job-title, [class*='title']",
        "link": "a[href]",
    },
    "Thales": {
        "url": "https://www.thalesgroup.com/fr/carrieres/nos-offres-d-emploi?job_type=apprentissage",
        "card": ".result-item, .job-item, [class*='job'], li",
        "title": "h2, h3, .job-title, [class*='title']",
        "link": "a[href]",
    },
    "Sopra Steria": {
        "url": "https://www.soprasteria.com/fr/carrieres/offres-emploi?type=alternance",
        "card": ".offer-card, .job-card, article, [class*='offer']",
        "title": "h2, h3, [class*='title'], [class*='job-name']",
        "link": "a[href]",
    },
    "Capgemini": {
        "url": "https://www.capgemini.com/fr-fr/carrieres/emplois/?search=cybersecurite&contract=alternance",
        "card": ".job-card, [class*='job'], [class*='offer'], li.result",
        "title": "h2, h3, [class*='title'], [class*='position']",
        "link": "a[href]",
    },
    "Stormshield": {
        "url": "https://www.stormshield.com/about-stormshield/careers/",
        "card": ".job, .offer, article, [class*='job'], [class*='career']",
        "title": "h2, h3, [class*='title']",
        "link": "a[href]",
    },
    "Claranet": {
        "url": "https://www.claranet.fr/carrieres",
        "card": ".job, .offer, article, [class*='job'], [class*='card']",
        "title": "h2, h3, [class*='title'], [class*='name']",
        "link": "a[href]",
    },
}

# Keywords to filter relevant cyber/alternance offers
RELEVANT_KEYWORDS = [
    "cyber", "sécurité", "security", "alternance", "apprentissage",
    "soc", "siem", "pentest", "réseau", "cloud", "devops",
]


class CompaniesScraper(BaseScraper):
    name = "companies"

    async def scrape(self) -> list[dict]:
        results = []
        tasks = [self._scrape_company(name, cfg) for name, cfg in COMPANIES.items()]
        company_results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in company_results:
            if isinstance(r, list):
                results += r
            elif isinstance(r, Exception):
                logger.warning(f"[companies] scraper error: {r}")
        logger.info(f"[companies] {len(results)} total jobs")
        return results

    async def _scrape_company(self, company_name: str, cfg: dict) -> list[dict]:
        results = []

        # Try API first if available (OVHcloud)
        if "api" in cfg:
            data = await self.fetch_json(cfg["api"])
            if data and isinstance(data, list):
                for job in data:
                    title = job.get("title", job.get("name", ""))
                    if not self._is_relevant(title + " " + job.get("description", "")):
                        continue
                    results.append({
                        "title": title,
                        "company": company_name,
                        "city": job.get("location", {}).get("city", "") if isinstance(job.get("location"), dict) else str(job.get("location", "")),
                        "url": job.get("url", job.get("apply_url", cfg["url"])),
                        "source": self.name,
                        "contract_type": job.get("contract_type", "Alternance"),
                        "description": job.get("description", "")[:500],
                    })
                if results:
                    logger.info(f"[companies] {company_name}: {len(results)} via API")
                    return results

        # HTML scraping
        html = await self.fetch(cfg["url"])
        if not html:
            return results

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(cfg["card"])

        if not cards:
            # Fallback: try to find any links with job-related text
            cards = soup.select("li, article, div[class]")

        for card in cards:
            title_el = card.select_one(cfg["title"])
            link_el = card.select_one(cfg["link"])
            if not title_el:
                continue

            title_text = title_el.get_text(strip=True)
            if not title_text or len(title_text) < 3:
                continue

            # Filter for relevant jobs
            if not self._is_relevant(title_text):
                continue

            href = link_el["href"] if link_el else ""
            # Resolve relative URLs
            if href.startswith("/"):
                from urllib.parse import urlparse
                base = urlparse(cfg["url"])
                href = f"{base.scheme}://{base.netloc}{href}"
            elif not href.startswith("http"):
                href = cfg["url"]

            results.append({
                "title": title_text,
                "company": company_name,
                "url": href,
                "source": self.name,
                "contract_type": "Alternance",
            })

        logger.info(f"[companies] {company_name}: {len(results)} jobs")
        return results

    def _is_relevant(self, text: str) -> bool:
        text_lower = text.lower()
        return any(kw in text_lower for kw in RELEVANT_KEYWORDS)


async def scrape_companies():
    return await CompaniesScraper().scrape()
