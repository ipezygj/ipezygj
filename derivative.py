""" Technical implementation for Hummingbot Gateway V2.1. """
import asyncio
import random
import time
from typing import Any, Dict, Optional
import httpx
from constants import (
    ALPHA_EXCHANGE_PAYLOAD, STEALTH_USER_AGENTS, STEALTH_LANGUAGES, 
    ADAPTIVE_JITTER_MS, FAILURE_THRESHOLD, COOLDOWN_PERIOD
)

class GatewayDerivativeConnector:
    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name.upper()
        self.base_url = ALPHA_EXCHANGE_PAYLOAD.get(self.exchange_name)
        self.error_count = 0
        self.cooldown_until = 0

    def is_available(self) -> bool:
        return time.time() > self.cooldown_until

    async def fetch_market_data(self, client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return {"exchange": self.exchange_name, "status": "COOLDOWN"}

        await asyncio.sleep(random.randint(*ADAPTIVE_JITTER_MS) / 1000.0)
        
        headers = {
            "User-Agent": random.choice(STEALTH_USER_AGENTS),
            "Accept-Language": random.choice(STEALTH_LANGUAGES),
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        start = time.time()
        try:
            resp = await client.get(self.base_url, headers=headers, timeout=5.0)
            resp.raise_for_status()
            self.error_count = 0  # Resetti onnistumisen jälkeen
            return {"exchange": self.exchange_name, "latency": int((time.time() - start) * 1000), "status": "OK"}
        except Exception:
            self.error_count += 1
            if self.error_count >= FAILURE_THRESHOLD:
                print(f"🚨 CIRCUIT BREAKER: {self.exchange_name} isolated for {COOLDOWN_PERIOD}s")
                self.cooldown_until = time.time() + COOLDOWN_PERIOD
            return {"exchange": self.exchange_name, "status": "ERROR"}

async def run_ultimate_diagnostics():
    print("🚀 V2.1 ULTIMATE ENGINE: Circuit Breakers & Meta-Stealth Active\n")
    async with httpx.AsyncClient() as client:
        connectors = [GatewayDerivativeConnector(ex) for ex in ALPHA_EXCHANGE_PAYLOAD.keys()]
        for cycle in range(1, 4):
            print(f"--- Cycle {cycle} ---")
            tasks = [c.fetch_market_data(client) for c in connectors]
            results = await asyncio.gather(*tasks)
            for r in results:
                status = r.get("status")
                lat = f"{r.get('latency')}ms" if status == "OK" else status
                print(f"📡 {r['exchange']:12} | {lat}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(run_ultimate_diagnostics())
