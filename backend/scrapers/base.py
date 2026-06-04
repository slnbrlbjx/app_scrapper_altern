"""Base scraper — shared HTTP helpers."""
import asyncio
import logging
import random
from abc import ABC, abstractmethod
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]

_BASE_HEADERS = {
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def _make_headers(json: bool = False) -> dict:
    return {
        **_BASE_HEADERS,
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept": "application/json" if json else "text/html,application/xhtml+xml,*/*;q=0.8",
    }


def make_client(json: bool = False) -> httpx.AsyncClient:
    """Return a configured AsyncClient. Use as: async with make_client() as client."""
    return httpx.AsyncClient(
        headers=_make_headers(json=json),
        follow_redirects=True,
        timeout=25,
    )


class BaseScraper(ABC):
    name: str = "base"

    @abstractmethod
    async def scrape(self) -> list[dict]:
        pass

    async def fetch(self, url: str, params: dict | None = None, client: httpx.AsyncClient | None = None) -> str | None:
        await asyncio.sleep(random.uniform(0.5, 1.5))
        if client is not None:
            return await self._get(client, url, params)
        async with make_client() as c:
            return await self._get(c, url, params)

    async def fetch_json(
        self,
        url: str,
        params: dict | None = None,
        json_body: dict | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> Any:
        await asyncio.sleep(random.uniform(0.3, 1.0))
        if client is not None:
            return await self._get_json(client, url, params, json_body)
        async with make_client(json=True) as c:
            return await self._get_json(c, url, params, json_body)

    async def _get(self, client: httpx.AsyncClient, url: str, params: dict | None) -> str | None:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.text
        except Exception as e:
            logger.warning("[%s] fetch failed %s: %s", self.name, url, e)
            return None

    async def _get_json(self, client: httpx.AsyncClient, url: str, params: dict | None, json_body: dict | None) -> Any:
        try:
            r = await (client.post(url, json=json_body) if json_body else client.get(url, params=params))
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning("[%s] fetch_json failed %s: %s", self.name, url, e)
            return None
