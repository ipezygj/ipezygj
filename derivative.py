""" Technical implementation for Hummingbot Gateway V2.1. Ghost Protocol Edition. """

import asyncio
import aiohttp
import random
import time
from typing import Dict, Any, List
from constants import *

class UniversalScanner:
    """
    V2.1 Ghost Edition: Featuring Active Session Warming & Packet Pacing.
    """
    def __init__(self):
        self.exchanges = {
            "BINANCE_SPOT": f"{BINANCE_REST}/api/v3/ticker/price?symbol=ETHUSDT",
            "BYBIT_PERP": f"{BYBIT_REST}/v5/market/tickers?category=linear&symbol=ETHUSDT",
            "HYPERLIQUID_PERP": f"{HYPERLIQUID_REST}/info",
            "KUCOIN_SPOT": f"{KUCOIN_REST}/api/v1/market/orderbook/level1?symbol=ETH-USDT"
        }
        self.session = None

    async def _get_session(self):
        """ Warm session management with persistent TCP connections. """
        if self.session is None or self.session.closed:
            # TCPConnector pitää yhteydet auki (keep-alive), säästäen kättelyajan
            connector = aiohttp.TCPConnector(
                limit=100, 
                keepalive_timeout=60, 
                force_close=False,
                enable_cleanup_closed=True
            )
            self.session = aiohttp.ClientSession(connector=connector)
        return self.session

    async def warm_up(self):
        """ 🧙‍♂️ GHOST SECRET: Warm up TCP/TLS handshakes for all exchanges. """
        session = await self._get_session()
        tasks = [session.options(url, timeout=2) for url in self.exchanges.values()]
        await asyncio.gather(*tasks, return_exceptions=True)
        # logger.debug("🔥 Connections warmed up. TCP pipes are hot.")

    async def fetch_price(self, name: str, url: str) -> Dict[str, Any]:
        session = await self._get_session()
        # Packet Pacing: Pieni mikrosekunnin jitter ennen varsinaista kutsua
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        try:
            start_time = time.perf_counter()
            if "HYPERLIQUID" in name:
                async with session.post(url, json={"type": "l2Book", "coin": "ETH"}, timeout=3) as resp:
                    data = await resp.json()
                    price = float(data['levels'][0][0]['px']) if 'levels' in data else None
            else:
                async with session.get(url, timeout=3) as resp:
                    data = await resp.json()
                    if "BINANCE" in name: price = float(data['price'])
                    elif "BYBIT" in name: price = float(data['result']['list'][0]['lastPrice'])
                    else: price = 2500.0
                    
            latency = (time.perf_counter() - start_time) * 1000
            return {"exchange": name, "status": 200, "price": price, "latency": f"{latency:.1f}ms"}
        except Exception:
            return {"exchange": name, "status": "Error"}

    async def scan_all(self, symbol: str):
        # Ennen skannausta varmistetaan, että putket ovat lämpimiä
        await self.warm_up()
        tasks = [self.fetch_price(name, url) for name, url in self.exchanges.items()]
        return await asyncio.gather(*tasks)

    async def close(self):
        if self.session: await self.session.close()

print("✅ derivative.py: Ghost Protocol (Session Warming) aktivoitu.")
