""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import aiohttp
import json
from typing import Dict, Any, List
from .auth import HyperliquidAuth
from .constants import HYPERLIQUID_REST

class HyperliquidDerivative:
    """
    V2.1 Stealth implementation for Hyperliquid CLOB/Perp.
    """
    def __init__(self, auth: HyperliquidAuth):
        self._auth = auth
        self._url = HYPERLIQUID_REST

    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """ Fetches L2 orderbook via Hyperliquid Info API. """
        payload = {
            "type": "l2Book",
            "coin": symbol
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self._url}/info", json=payload) as response:
                if response.status == 200:
                    return await response.json()
                return {"error": response.status}

print("✅ derivative.py päivitetty: Markkinadata-yhteys valmis.")
