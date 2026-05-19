import httpx
import os
import logging

logger = logging.getLogger(__name__)
WEBHOOK = os.getenv("DISCORD_WEBHOOK", "")


async def send_discord_alert(job: dict):
    if not WEBHOOK:
        logger.debug("No Discord webhook configured — skipping alert")
        return

    title = job.get("title", "Offre sans titre")
    company = job.get("company", "")
    url = job.get("url", "")
    source = job.get("source", "")
    contract = job.get("contract_type", "")
    city = job.get("city", "")

    lines = [
        f"🔐 **Nouvelle offre** [{source}]",
        f"**{title}**",
    ]
    if company:
        lines.append(f"🏢 {company}")
    if city:
        lines.append(f"📍 {city}")
    if contract:
        lines.append(f"📄 {contract}")
    if url:
        lines.append(f"🔗 {url}")

    payload = {"content": "\n".join(lines)}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(WEBHOOK, json=payload)
            r.raise_for_status()
    except Exception as e:
        logger.warning(f"Discord webhook error: {e}")
