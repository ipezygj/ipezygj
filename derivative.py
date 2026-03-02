""" Technical implementation for Hummingbot Gateway V2.1. Global Awakening Edition. """

import asyncio
import aiohttp
import random
import time
from typing import Dict, Any

class UniversalScanner:
    def __init__(self):
        # Päivitetty lista: Käytetään varmimpia julkisia endpointeja
        self.exchanges = {
            "BINANCE_SPOT": "https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT",
            "BYBIT_PERP": "https://api.bybit.com/v5/market/tickers?category=linear&symbol=ETHUSDT",
            "KUCOIN_SPOT": "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=ETH-USDT",
            "GATE_IO": "https://api.gateio.ws/api/v4/spot/tickers?currency_pair=ETH_USDT",
            "MEXC_SPOT": "https://api.mexc.com/api/v3/ticker/price?symbol=ETHUSDT",
            "OKX_SPOT": "https://www.okx.com/api/v5/market/ticker?instId=ETH-USDT"
        }
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        self.session = None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self.session

    async def fetch_price(self, name: str, url: str) -> Dict[str, Any]:
        session = await self._get_session()
        await asyncio.sleep(random.uniform(0.05, 0.1)) # Stealth jitter
        
        try:
            start = time.perf_counter()
            async with session.get(url, timeout=5) as resp:
                data = await resp.json()
                price = None
                
                # Dynaaminen hinnan uutto eri JSON-rakenteista
                if "BINANCE" in name or "MEXC" in name: price = float(data['price'])
                elif "BYBIT" in name: price = float(data['result']['list'][0]['lastPrice'])
                elif "KUCOIN" in name: price = float(data['data']['price'])
                elif "GATE" in name: price = float(data[0]['last'])
                elif "OKX" in name: price = float(data['data'][0]['last'])
                
                lat = (time.perf_counter() - start) * 1000
                return {"exchange": name, "status": 200, "price": price, "latency": f"{lat:.1f}ms", "type": "SPOT" if "SPOT" in name else "PERP"}
        except Exception:
            return {"exchange": name, "status": "Error"}

    async def scan_all(self, symbol: str):
        tasks = [self.fetch_price(name, url) for name, url in self.exchanges.items()]
        return await asyncio.gather(*tasks)

    async def close(self):
        if self.session: await self.session.close()

print("✅ derivative.py: Global Awakening (Multi-Exchange fix) aktivoitu.")
