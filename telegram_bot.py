""" Technical implementation for Hummingbot Gateway V2.1. """
import asyncio

import httpx

from auth import ALPHA_CHAT_ID, COSMIC_CHAT_ID, TELEGRAM_TOKEN


async def send_alpha_alert(message: str, channel: str = "alpha") -> bool:
    """ Reitittää viestin oikeaan ryhmään (alpha tai cosmic). """
    target_id = COSMIC_CHAT_ID if channel == "cosmic" else ALPHA_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data_payload = {"chat_id": target_id, "text": message, "parse_mode": "Markdown"}
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json=data_payload, timeout=10.0)
            return r.status_code == 200
        except Exception as e:
            print(f"❌ [BOT] Network error: {e}")
            return False
