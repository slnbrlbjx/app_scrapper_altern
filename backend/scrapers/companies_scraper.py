"""Cyber companies career pages scraper."""
import asyncio
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, make_client
from services.filter import is_cyber_job

logger = logging.getLogger(__name__)

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


class CompaniesScraper(BaseScraper):
    name = "companies"

    async def scrape(self) -> list[dict]:
        # One shared client for all companies — sequential to avoid hammering sites
        async with make_client() as html_client, make_client(json=True) as api_client:
            tasks = [
                self._scrape_company(name, cfg, html_client, api_client)
                for name, cfg in COMPANIES.items()
            ]
            company_results = await asyncio.gather(*tasks, return_exceptions=True)

        results = []
        for r in company_results:
            if isinstance(r, list):
                results += r
            elif isinstance(r, Exception):
                logger.warning("[companies] scraper error: %s", r)
        logger.info("[companies] %d total jobs", len(results))
        return results

    async def _scrape_company(
        self, company_name: str, cfg: dict,
        html_client, api_client,
    ) -> list[dict]:
        # Try API first if available (OVHcloud)
        if "api" in cfg:
            data = await self.fetch_json(cfg["api"], client=api_client)
            if data and isinstance(data, list):
                results = []
                for job in data:
                    title = job.get("title", job.get("name", ""))
                    if not is_cyber_job(title + " " + job.get("description", "")):
                        continue
                    loc = job.get("location", {})
                    results.append({
                        "title": title,
                        "company": company_name,
                        "city": loc.get("city", "") if isinstance(loc, dict) else str(loc),
                        "url": job.get("url", job.get("apply_url", cfg["url"])),
                        "source": self.name,
                        "contract_type": job.get("contract_type", "Alternance"),
                        "description": job.get("description", "")[:500],
                    })
                if results:
                    logger.info("[companies] %s: %d via API", company_name, len(results))
                    return results

        html = await self.fetch(cfg["url"], client=html_client)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        cards = soup.select(cfg["card"]) or soup.select("li, article, div[class]")
        base = urlparse(cfg["url"])

        results = []
        for card in cards:
            title_el = card.select_one(cfg["title"])
            link_el = card.select_one(cfg["link"])
            if not title_el:
                continue
            title_text = title_el.get_text(strip=True)
            if len(title_text) < 3 or not is_cyber_job(title_text):
                continue
            href = link_el["href"] if link_el else ""
            if href.startswith("/"):
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
        logger.info("[companies] %s: %d jobs", company_name, len(results))
        return results


async def scrape_companies():
    return await CompaniesScraper().scrape()
