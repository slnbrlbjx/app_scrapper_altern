import httpx
import os

WEBHOOK = os.getenv("DISCORD_WEBHOOK")


async def send_discord_alert(job):
    payload = {
        "content": (
            f"🚨 Nouvelle alternance cyber\n"
            f"{job['title']}\n"
            f"{job['company']}\n"
            f"{job['url']}"
        )
    }

    async with httpx.AsyncClient() as client:
        await client.post(WEBHOOK, json=payload)