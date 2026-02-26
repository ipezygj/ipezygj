""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import random
import time
from typing import Any, Dict, Optional

import httpx

from constants import (
    ALPHA_EXCHANGE_PAYLOAD, 
    NETWORK_TIMEOUT_CRITICAL, 
    STEALTH_HEADERS,
    MAX_CONNECTIONS,
    MAX_KEEP_ALIVE_CONNECTIONS,
    ADAPTIVE_JITTER_MS
)

class GatewayDerivativeConnector:
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name.upper()
        self.base_url = ALPHA_EXCHANGE_PAYLOAD.get(self.exchange_name)
        if not self.base_url:
            raise ValueError(f"Exchange {self.exchange_name} not found.")

    async def fetch_market_data(self, client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
        # Adaptive Jitter: Lisätään inhimillinen satunnaisuus
        jitter = random.randint(*ADAPTIVE_JITTER_MS) / 1000.0
        await asyncio.sleep(jitter)
        
        start_time = time.time()
        try:
            response = await client.get(
                self.base_url,
                headers=STEALTH_HEADERS,
                timeout=NETWORK_TIMEOUT_CRITICAL
            )
            response.raise_for_status()
            return {
                "status": "ONLINE", 
                "latency_ms": int((time.time() - start_time) * 1000), 
                "exchange": self.exchange_name
            }
        except Exception:
            return None

async def run_optimized_diagnostics():
    # Connection Pooling: Luodaan rajoitukset clienteille
    limits = httpx.Limits(
        max_connections=MAX_CONNECTIONS, 
        max_keepalive_connections=MAX_KEEP_ALIVE_CONNECTIONS
    )
    
    print(f"🚀 Initializing V2.1 Optimized Engine [Pooler + Jitter Active]...\n")
    
    async with httpx.AsyncClient(limits=limits) as client:
        test_exchanges = list(ALPHA_EXCHANGE_PAYLOAD.keys())[:5]
        tasks = [GatewayDerivativeConnector(ex).fetch_market_data(client) for ex in test_exchanges]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            if res:
                print(f"✅ OPTIMIZED: {res['exchange']:12} | Latency: {res['latency_ms']}ms")

if __name__ == "__main__":
    asyncio.run(run_optimized_diagnostics())
