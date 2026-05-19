# Alternance Scrapper

Agrégateur automatique d'offres d'alternance (en cybersécurité).

## Sources couvertes

### Job boards
| Source | Méthode |
|---|---|
| LinkedIn | HTML public |
| Welcome to the Jungle | API publique + HTML fallback |
| Hellowork | HTML |
| APEC | API JSON + HTML fallback |
| Indeed | HTML |
| LesJeudis | HTML |
| France Travail | API officielle + HTML fallback |

### Réseaux sociaux
| Source | Méthode |
|---|---|
| Reddit | API JSON publique (no auth) |
| X / Twitter | Nitter RSS (instances publiques) |
| LinkedIn Posts | DuckDuckGo index |
| Discord | Disboard.org |
| Telegram | t.me/s/ (canaux publics) |

### Entreprises cyber
Advens · OVHcloud · Orange Cyberdefense · Thales · Sopra Steria · Capgemini · Stormshield · Claranet

---

## Lancement rapide

```bash
# Copier et configurer l'environnement
cp .env .env.local

# (optionnel) Remplir DISCORD_WEBHOOK, FRANCE_TRAVAIL_CLIENT_ID, etc.

# Démarrer tout
docker compose up --build
```

- Frontend : http://localhost:3000
- API : http://localhost:8000
- Docs API : http://localhost:8000/docs

## Variables d'environnement

| Variable | Requis | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | URL PostgreSQL |
| `DISCORD_WEBHOOK` | ❌ | URL webhook Discord pour alertes |
| `FRANCE_TRAVAIL_CLIENT_ID` | ❌ | Clé API France Travail (inscription gratuite) |
| `FRANCE_TRAVAIL_CLIENT_SECRET` | ❌ | Secret API France Travail |
| `REDDIT_CLIENT_ID` | ❌ | Clé API Reddit (optionnel, le scraper fonctionne sans) |

## Architecture

```
backend/
  main.py              # FastAPI app
  api/routes/jobs.py   # Endpoints REST
  database/database.py # SQLAlchemy + helpers
  models/job.py        # Modèle Job
  scrapers/            # Un fichier par source
  services/
    discord.py         # Alertes Discord
    filter.py          # Filtrage par mots-clés
    keywords.py        # Liste de mots-clés cyber
worker/
  scheduler.py         # APScheduler — toutes les 30 min
frontend/
  app/page.tsx         # Dashboard Next.js
```
 
