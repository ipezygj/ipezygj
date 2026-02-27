""" Technical implementation for Hummingbot Gateway V2.1. """
import httpx
from auth import TELEGRAM_TOKEN, ALPHA_CHAT_ID, COSMIC_CHAT_ID, VIP_CHAT_ID

async def send_alpha_alert(message: str, channel: str = "alpha") -> bool:
    """ Routes payloads to specific Telegram channels. """
    
    # Valitaan ID muuttujasta, ei kovakoodattuna
    target_map = {
        "vip": VIP_CHAT_ID,
        "cosmic": COSMIC_CHAT_ID,
        "alpha": ALPHA_CHAT_ID
    }
    chat_id = target_map.get(channel, ALPHA_CHAT_ID)

    # Rakennetaan URL dynaamisesti
    base_url = "https://api.telegram.org"
    send_url = f"{base_url}/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(send_url, json=payload, timeout=10.0)
            return r.status_code == 200
        except Exception as e:
            print(f"❌ [TELEGRAM] Transmission failed")
            return False
