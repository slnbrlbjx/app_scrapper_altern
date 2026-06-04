"""LinkedIn posts scraper — DuckDuckGo HTML search (no API key needed)."""
import logging
import urllib.parse
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, make_client

logger = logging.getLogger(__name__)

QUERIES = [
    'site:linkedin.com/posts "alternance" "cybersécurité"',
    'site:linkedin.com/posts "alternance" "sécurité informatique"',
]


class LinkedInPostsScraper(BaseScraper):
    name = "linkedin_posts"

    async def scrape(self) -> list[dict]:
        results = []
        async with make_client() as client:
            for q in QUERIES:
                html = await self.fetch(
                    "https://html.duckduckgo.com/html/",
                    params={"q": q, "kl": "fr-fr"},
                    client=client,
                )
                if not html:
                    continue
                soup = BeautifulSoup(html, "html.parser")
                for result in soup.select(".result"):
                    title_el = result.select_one(".result__title")
                    link_el = result.select_one("a.result__url, a[href*='linkedin.com']")
                    snippet_el = result.select_one(".result__snippet")
                    if not title_el:
                        continue
                    href = ""
                    if link_el:
                        href = link_el.get("href", "")
                        if "uddg=" in href:
                            qs = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                            href = qs.get("uddg", [""])[0]
                    if "linkedin.com" not in href:
                        continue
                    results.append({
                        "title": title_el.get_text(strip=True),
                        "company": "",
                        "url": href,
                        "source": self.name,
                        "description": snippet_el.get_text(strip=True) if snippet_el else "",
                        "contract_type": "Post",
                    })
        logger.info("[linkedin_posts] %d posts", len(results))
        return results


async def scrape_linkedin_posts():
    return await LinkedInPostsScraper().scrape()
