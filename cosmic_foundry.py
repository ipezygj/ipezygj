""" Technical implementation for Hummingbot Gateway V2.1. """
import asyncio

import httpx

from auth import NASA_API_KEY
from telegram_bot import send_alpha_alert


async def fetch_cosmic_data():
    """ Hakee NASA:n uutisvirran ja lähettää sen Cosmic Interface -kanavalle. """
    url = f"https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}"
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, timeout=15.0)
            if r.status_code == 200:
                data = r.json()
                msg = f"🌌 *COSMIC INTERFACE UPLINK*\n📍 {data.get('title')}\n📡 {data.get('explanation')[:200]}..."
                
                await send_alpha_alert(msg, channel="cosmic")
                print("🌌 [COSMIC] Uutinen reititetty Cosmic Interface -ryhmään.")
        except Exception:
            pass
