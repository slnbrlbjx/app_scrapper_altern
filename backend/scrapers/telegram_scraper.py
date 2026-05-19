"""Telegram public channels scraper.

Telegram public channels can be read without auth via t.me/s/<channel>.
We scrape known cybersecurity / emploi French channels.
"""
import logging
import re
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# Known public French cybersecurity & emploi Telegram channels
PUBLIC_CHANNELS = [
    "cybersecfr",          # French cybersecurity community
    "emploi_cyber",        # Cyber job postings
    "alternance_cyber",    # Alternance cyber (may or may not exist)
    "offresCyber",         # Job offers
    "FranceSecurite",      # French security news
]

BASE_URL = "https://t.me/s/{channel}"


class TelegramScraper(BaseScraper):
    name = "telegram"

    async def scrape(self) -> list[dict]:
        results = []
        for channel in PUBLIC_CHANNELS:
            posts = await self._scrape_channel(channel)
            results += posts
        logger.info(f"[telegram] {len(results)} posts total")
        return results

    async def _scrape_channel(self, channel: str) -> list[dict]:
        url = BASE_URL.format(channel=channel)
        html = await self.fetch(url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []

        for msg in soup.select(".tgme_widget_message"):
            text_el = msg.select_one(".tgme_widget_message_text")
            date_el = msg.select_one("time")
            link_el = msg.select_one("a.tgme_widget_message_date")

            if not text_el:
                continue

            text = text_el.get_text(strip=True)
            # Filter: only keep posts mentioning alternance or job-related content
            keywords = ["alternance", "stage", "cdi", "cdd", "recrutement", "emploi",
                        "cybersécurité", "cyber", "sécurité", "soc", "pentest"]
            if not any(kw in text.lower() for kw in keywords):
                continue

            msg_url = link_el["href"] if link_el else url
            # Try to extract a title (first line or first 100 chars)
            title = text.split("\n")[0][:150] if "\n" in text else text[:150]

            results.append({
                "title": title,
                "company": f"@{channel}",
                "url": msg_url,
                "source": self.name,
                "description": text[:500],
                "contract_type": "Post",
            })

        logger.info(f"[telegram] {len(results)} posts from @{channel}")
        return results


async def scrape_telegram():
    return await TelegramScraper().scrape()
