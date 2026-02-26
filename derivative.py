""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import time
from typing import Any, Dict, Optional

import httpx

from constants import ALPHA_EXCHANGE_PAYLOAD, NETWORK_TIMEOUT_CRITICAL, STEALTH_HEADERS


class GatewayDerivativeConnector:
    """
    V2.1 Institutional Grade Async Connector.
    Handles high-frequency orderbook and market data fetching using modular payloads.
    """

    def __init__(self, exchange_name: str):
        self.exchange_name = exchange_name.upper()
        self.base_url = ALPHA_EXCHANGE_PAYLOAD.get(self.exchange_name)
        
        if not self.base_url:
            raise ValueError(f"CRITICAL ERROR: Exchange {self.exchange_name} not found in constants data_payload.")

    async def fetch_market_data(self, client: httpx.AsyncClient) -> Optional[Dict[str, Any]]:
        """
        Async fetch operation using the V2.1 stealth payload and critical timeouts.
        """
        start_time = time.time()
        try:
            response = await client.get(
                self.base_url,
                headers=STEALTH_HEADERS,
                timeout=NETWORK_TIMEOUT_CRITICAL
            )
            response.raise_for_status()
            latency = int((time.time() - start_time) * 1000)
            return {"status": "ONLINE", "latency_ms": latency, "exchange": self.exchange_name}
        except httpx.HTTPError as e:
            print(f"🛑 [DERIVATIVE ENGINE] Network failure to {self.exchange_name}: {e}")
            return None
        except Exception as e:
            print(f"🛑 [DERIVATIVE ENGINE] Unexpected failure: {e}")
            return None


async def run_derivative_diagnostics():
    """ 
    Diagnostic run: Test the derivative engine using a high-speed async gather 
    on the first three Alpha exchanges.
    """
    test_exchanges = list(ALPHA_EXCHANGE_PAYLOAD.keys())[:3]
    print(f"🏎️ Revving up the V2.1 Derivative Engine for {test_exchanges}...\n")
    
    async with httpx.AsyncClient() as client:
        tasks = [
            GatewayDerivativeConnector(ex).fetch_market_data(client) 
            for ex in test_exchanges
        ]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            if res:
                print(f"✅ CORE CONNECTED: {res['exchange']:12} | Data Stream Latency: {res['latency_ms']}ms")


if __name__ == "__main__":
    asyncio.run(run_derivative_diagnostics())
