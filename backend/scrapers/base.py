"""Base scraper class with shared helpers."""
import httpx
import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class BaseScraper(ABC):
    name: str = "base"

    @abstractmethod
    async def scrape(self) -> list[dict]:
        pass

    async def fetch(self, url: str, params: dict = None) -> str | None:
        try:
            async with httpx.AsyncClient(
                headers=HEADERS, follow_redirects=True, timeout=20
            ) as client:
                r = await client.get(url, params=params)
                r.raise_for_status()
                return r.text
        except Exception as e:
            logger.warning(f"[{self.name}] fetch error {url}: {e}")
            return None

    async def fetch_json(self, url: str, params: dict = None, json_body: dict = None) -> dict | None:
        try:
            async with httpx.AsyncClient(
                headers={**HEADERS, "Accept": "application/json"},
                follow_redirects=True,
                timeout=20,
            ) as client:
                if json_body:
                    r = await client.post(url, json=json_body)
                else:
                    r = await client.get(url, params=params)
                r.raise_for_status()
                return r.json()
        except Exception as e:
            logger.warning(f"[{self.name}] fetch_json error {url}: {e}")
            return None
