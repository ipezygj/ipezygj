""" Technical implementation for Hummingbot Gateway V2.1. """
import httpx
from auth import TELEGRAM_TOKEN, ALPHA_CHAT_ID, COSMIC_CHAT_ID, VIP_CHAT_ID

async def send_alpha_alert(message: str, channel: str = "alpha") -> bool:
    """ Routes payloads to specific Telegram channels based on source engine. """
    
    # Valitaan oikea putki
    if channel == "vip":
        chat_id = VIP_CHAT_ID
    elif channel == "cosmic":
        chat_id = COSMIC_CHAT_ID
    else:
        chat_id = ALPHA_CHAT_ID

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(url, json=payload, timeout=10.0)
            return r.status_code == 200
        except Exception as e:
            print(f"❌ [TELEGRAM] Transmission failed: {e}")
            return False
