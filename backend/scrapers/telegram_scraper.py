"""Telegram public channels scraper via t.me/s/<channel>."""
import logging
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, make_client
from services.filter import is_cyber_job

logger = logging.getLogger(__name__)

PUBLIC_CHANNELS = [
    "cybersecfr",
    "emploi_cyber",
    "alternance_cyber",
    "offresCyber",
    "FranceSecurite",
]


class TelegramScraper(BaseScraper):
    name = "telegram"

    async def scrape(self) -> list[dict]:
        results = []
        async with make_client() as client:
            for channel in PUBLIC_CHANNELS:
                results += await self._scrape_channel(channel, client)
        if not results:
            logger.warning("[telegram] 0 posts returned")
        logger.info("[telegram] %d posts total", len(results))
        return results

    async def _scrape_channel(self, channel: str, client) -> list[dict]:
        url = f"https://t.me/s/{channel}"
        html = await self.fetch(url, client=client)
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for msg in soup.select(".tgme_widget_message"):
            text_el = msg.select_one(".tgme_widget_message_text")
            link_el = msg.select_one("a.tgme_widget_message_date")
            if not text_el:
                continue
            text = text_el.get_text(strip=True)
            if not is_cyber_job(text):
                continue
            title = text.split("\n")[0][:150] if "\n" in text else text[:150]
            results.append({
                "title": title,
                "company": f"@{channel}",
                "url": link_el["href"] if link_el else url,
                "source": self.name,
                "description": text[:500],
                "contract_type": "Post",
            })
        logger.info("[telegram] %d posts from @%s", len(results), channel)
        return results


async def scrape_telegram():
    return await TelegramScraper().scrape()
