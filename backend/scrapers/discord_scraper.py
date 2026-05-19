"""Discord public servers scraper.

Discord doesn't have a public search API for messages.
We scrape public Discord servers listed on disboard.org and
public "job board" channels that are indexed by third-party aggregators.
"""
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# Disboard: public Discord server directory
DISBOARD_URL = "https://disboard.org/servers/tag/cybersecurity"
DISBOARD_FR_URL = "https://disboard.org/servers/tag/cybersecurite"

# Public Discord job aggregators / announcement feeds
DISCORD_JOB_SOURCES = [
    "https://disboard.org/servers/tag/emploi-informatique",
    "https://disboard.org/servers/tag/alternance",
]


class DiscordScraper(BaseScraper):
    name = "discord"

    async def scrape(self) -> list[dict]:
        results = []
        for url in [DISBOARD_URL, DISBOARD_FR_URL] + DISCORD_JOB_SOURCES:
            html = await self.fetch(url)
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
                # Only keep servers mentioning cyber/security topics
                if not any(kw in desc_text.lower() for kw in ["cyber", "sécurité", "security", "alternance", "emploi"]):
                    continue
                href = link_el["href"] if link_el else ""
                results.append({
                    "title": f"Serveur Discord: {name_el.get_text(strip=True)}",
                    "company": "Discord",
                    "url": href,
                    "source": self.name,
                    "description": desc_text[:500],
                    "contract_type": "Communauté",
                })
        logger.info(f"[discord] {len(results)} servers/posts")
        return results


async def scrape_discord():
    return await DiscordScraper().scrape()
