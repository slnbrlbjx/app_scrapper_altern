"""APEC scraper — official public JSON API."""
import logging
from scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

# APEC public search API (no auth required for basic search)
API_URL = "https://www.apec.fr/cms/webservices/rechercheOffre/rechercheOffre"


class APECScraper(BaseScraper):
    name = "apec"

    async def scrape(self) -> list[dict]:
        results = []
        payload = {
            "motsCles": "cybersécurité alternance",
            "typeContrat": [["ALTERNANCE"]],
            "nombreParPage": 50,
            "pageCourante": 0,
            "tris": [{"type": "DATE", "order": "DESC"}],
        }
        data = await self.fetch_json(API_URL, json_body=payload)
        if data:
            for offer in data.get("resultats", []):
                results.append({
                    "title": offer.get("intitule", ""),
                    "company": offer.get("nomEntreprise", ""),
                    "city": offer.get("lieuTravail", {}).get("libelle", ""),
                    "url": f"https://www.apec.fr/candidat/recherche-emploi.html/emploi/{offer.get('numeroOffre', '')}",
                    "source": self.name,
                    "contract_type": "Alternance",
                    "description": offer.get("texteOffre", ""),
                    "salary": offer.get("salaireTexte", ""),
                })
        else:
            # HTML fallback
            results += await self._scrape_html()

        logger.info(f"[apec] {len(results)} jobs")
        return results

    async def _scrape_html(self) -> list[dict]:
        from bs4 import BeautifulSoup
        url = "https://www.apec.fr/candidat/recherche-emploi.html"
        html = await self.fetch(url, params={
            "motsCles": "cybersécurité",
            "typeContrat": "ALTERNANCE",
        })
        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for card in soup.select(".card-offer, [class*='offer-card']"):
            title_el = card.select_one("h2, h3, .offer-title")
            company_el = card.select_one(".company-name, [class*='company']")
            link_el = card.select_one("a[href]")
            if not title_el:
                continue
            href = link_el["href"] if link_el else ""
            results.append({
                "title": title_el.get_text(strip=True),
                "company": company_el.get_text(strip=True) if company_el else "",
                "url": f"https://www.apec.fr{href}" if href.startswith("/") else href,
                "source": self.name,
                "contract_type": "Alternance",
            })
        return results


async def scrape_apec():
    return await APECScraper().scrape()
