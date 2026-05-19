"""France Travail (Pôle Emploi) scraper — official API v2."""
import logging
import os
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# France Travail API requires client credentials (free registration)
# https://francetravail.io/produits-et-services/api
TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token"
SEARCH_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search"

CLIENT_ID = os.getenv("FRANCE_TRAVAIL_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET", "")


class FranceTravailScraper(BaseScraper):
    name = "france_travail"
    _token: str | None = None

    async def _get_token(self) -> str | None:
        if not CLIENT_ID or not CLIENT_SECRET:
            logger.warning("[france_travail] No API credentials, using HTML fallback")
            return None
        import httpx
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    TOKEN_URL,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": CLIENT_ID,
                        "client_secret": CLIENT_SECRET,
                        "scope": "api_offresdemploiv2 o2dsoffre",
                    },
                    params={"realm": "/partenaire"},
                )
                r.raise_for_status()
                return r.json().get("access_token")
        except Exception as e:
            logger.warning(f"[france_travail] Token error: {e}")
            return None

    async def scrape(self) -> list[dict]:
        token = await self._get_token()
        if token:
            return await self._scrape_api(token)
        return await self._scrape_html()

    async def _scrape_api(self, token: str) -> list[dict]:
        import httpx
        results = []
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(
                    SEARCH_URL,
                    headers={"Authorization": f"Bearer {token}"},
                    params={
                        "motsCles": "cybersécurité",
                        "typeContrat": "A",  # A = Alternance/Apprentissage
                        "range": "0-49",
                        "sort": "1",
                    },
                )
                r.raise_for_status()
                data = r.json()
                for offer in data.get("resultats", []):
                    lieu = offer.get("lieuTravail", {})
                    results.append({
                        "title": offer.get("intitule", ""),
                        "company": offer.get("entreprise", {}).get("nom", ""),
                        "city": lieu.get("libelle", ""),
                        "url": offer.get("origineOffre", {}).get("urlOrigine", f"https://candidat.francetravail.fr/offres/recherche/detail/{offer.get('id', '')}"),
                        "source": self.name,
                        "contract_type": "Alternance",
                        "description": offer.get("description", ""),
                        "salary": offer.get("salaire", {}).get("libelle", ""),
                    })
        except Exception as e:
            logger.warning(f"[france_travail] API error: {e}")
        logger.info(f"[france_travail] {len(results)} jobs via API")
        return results

    async def _scrape_html(self) -> list[dict]:
        from bs4 import BeautifulSoup
        html = await self.fetch(
            "https://candidat.francetravail.fr/offres/recherche",
            params={
                "motsCles": "cybersécurité",
                "typeContrat": "A",
            },
        )
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for card in soup.select("li.result"):
            title_el = card.select_one("h2, h3, .offer-title")
            company_el = card.select_one(".company, [class*='company']")
            link_el = card.select_one("a[href]")
            if not title_el:
                continue
            href = link_el["href"] if link_el else ""
            results.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "url": f"https://candidat.francetravail.fr{href}" if href.startswith("/") else href,
                "source": self.name,
                "contract_type": "Alternance",
            })
        logger.info(f"[france_travail] {len(results)} jobs via HTML")
        return results


async def scrape_francetravail():
    return await FranceTravailScraper().scrape()
