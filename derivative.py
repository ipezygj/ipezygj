""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import aiohttp
import random
from typing import Dict, Any, List
from .constants import *

class UniversalScanner:
    """
    V2.1 Stealth Scanner with jitter and staggering.
    Designed to bypass exchange bot-detection.
    """
    def __init__(self):
        self.exchanges = {
            "HYPERLIQUID": HYPERLIQUID_REST,
            "BINANCE": BINANCE_REST,
            "KUCOIN": KUCOIN_REST,
            "OKX": OKX_REST,
            "BYBIT": BYBIT_REST,
            "KRAKEN": KRAKEN_REST,
            "MEXC": MEXC_REST,
            "GATE_IO": GATE_IO_REST,
            "ASCEND_EX": ASCEND_EX_REST,
            "PHEMEX": PHEMEX_REST,
            "HUOBI": HUOBI_REST
        }

    async def fetch_price(self, session: aiohttp.ClientSession, name: str, url: str, symbol: str) -> Dict[str, Any]:
        """ Individual fetch with random stagger. """
        # Lisätään pieni satunnainen viive ennen kutsua (0.1 - 0.5s)
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        try:
            # Tässä kohtaa toteutetaan pörssikohtaiset endpointit myöhemmin
            # Nyt käytetään Hyperliquid-mallia esimerkkinä
            target = f"{url}/info" if "hyperliquid" in url else url
            async with session.get(target, timeout=5) as response:
                return {"exchange": name, "status": response.status}
        except Exception as e:
            return {"exchange": name, "error": str(e)}

    async def scan_all(self, symbol: str):
        """ Scans all exchanges with non-linear staggering. """
        async with aiohttp.ClientSession() as session:
            # Sekoitetaan pörssien järjestys joka kerta
            names = list(self.exchanges.keys())
            random.shuffle(names)
            
            tasks = []
            for name in names:
                tasks.append(self.fetch_price(session, name, self.exchanges[name], symbol))
                # Porrastetaan kutsujen aloitus (0.2 - 0.7s välein)
                await asyncio.sleep(random.uniform(0.2, 0.7))
            
            results = await asyncio.gather(*tasks)
            return results

print("✅ derivative.py: Universaali Stealth-skanneri luotu.")
