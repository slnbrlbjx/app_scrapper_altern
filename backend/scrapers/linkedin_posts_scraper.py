"""LinkedIn Posts scraper — scrapes public posts via Google search (LinkedIn blocks direct scraping)."""
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

QUERIES = [
    'site:linkedin.com/posts "alternance" "cybersécurité"',
    'site:linkedin.com/posts "alternance" "sécurité informatique"',
]


class LinkedInPostsScraper(BaseScraper):
    name = "linkedin_posts"

    async def scrape(self) -> list[dict]:
        results = []
        for q in QUERIES:
            # Use DuckDuckGo HTML search (no JS, no API key needed)
            html = await self.fetch(
                "https://html.duckduckgo.com/html/",
                params={"q": q, "kl": "fr-fr"},
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
                    # DuckDuckGo wraps URLs in redirect
                    if "uddg=" in href:
                        import urllib.parse
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
        logger.info(f"[linkedin_posts] {len(results)} posts")
        return results


async def scrape_linkedin_posts():
    return await LinkedInPostsScraper().scrape()
