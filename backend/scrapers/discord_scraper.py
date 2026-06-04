"""Discord public servers scraper via disboard.org."""
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, make_client
from services.filter import is_cyber_job

logger = logging.getLogger(__name__)

SOURCES = [
    "https://disboard.org/servers/tag/cybersecurity",
    "https://disboard.org/servers/tag/cybersecurite",
    "https://disboard.org/servers/tag/emploi-informatique",
    "https://disboard.org/servers/tag/alternance",
]


class DiscordScraper(BaseScraper):
    name = "discord"

    async def scrape(self) -> list[dict]:
        results = []
        async with make_client() as client:
            for url in SOURCES:
                html = await self.fetch(url, client=client)
                if not html:
                    continue
                soup = BeautifulSoup(html, "html.parser")
                for card in soup.select(".server-card, [class*='server']"):
                    name_el = card.select_one(".server-name, h3, h2")
                    desc_el = card.select_one(".server-description, p")
                    link_el = card.select_one("a[href*='discord.gg'], a[href*='discord.com']")
                    if not name_el:
                        continue
                    desc_text = desc_el.get_text(strip=True) if desc_el else ""
                    if not is_cyber_job(desc_text):
                        continue
                    results.append({
                        "title": f"Serveur Discord: {name_el.get_text(strip=True)}",
                        "company": "Discord",
                        "url": link_el["href"] if link_el else "",
                        "source": self.name,
                        "description": desc_text[:500],
                        "contract_type": "Communauté",
                    })
        logger.info("[discord] %d servers/posts", len(results))
        return results


async def scrape_discord():
    return await DiscordScraper().scrape()
