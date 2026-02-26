""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import json
import websockets
from .auth import HyperliquidAuth
from .constants import INFO_URL

class HyperliquidDerivative:
    """
    Main execution class for Hyperliquid V2.1.
    Handles order placement and real-time WebSocket streams with EIP-712 security.
    """

    def __init__(self, auth: HyperliquidAuth):
        self.auth = auth
        self.ws_url = "wss://api.hyperliquid.xyz/ws"
        self.order_book = {}

    async def listen_to_order_book(self, symbol: str):
        """
        Maintains a real-time L2 order book via WebSocket.
        """
        subscribe_payload = {
            "method": "subscribe",
            "subscription": {"type": "l2Book", "coin": symbol}
        }
        
        async with websockets.connect(self.ws_url) as ws:
            await ws.send(json.dumps(subscribe_payload))
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                self.order_book[symbol] = data.get("data")

    async def create_order(self, symbol: str, price: float, amount: float, side: str):
        """
        Creates and signs a limit order using EIP-712 for Hyperliquid L1.
        """
        nonce = self.auth.get_current_nonce()
        
        # Rakennetaan Hyperliquid-spesifinen kaupankäyntitoiminto
        action = {
            "type": "order",
            "orders": [{
                "asset": 0,  # Oletusomaisuus (esim. USDC/HYPE)
                "isBuy": side.lower() == "buy",
                "limitPx": str(price),
                "sz": str(amount),
                "reduceOnly": False,
                "orderType": {"limit": {"tif": "Gtc"}}
            }],
            "grouping": "na"
        }

        # Allekirjoitetaan toiminto Ferrari-moottorillamme
        signature = self.auth.sign_action(action, nonce)
        
        payload = {
            "action": action,
            "nonce": nonce,
            "signature": signature
        }

        # TODO: Lähetä payload pörssin API-endpointtiin
        print(f"Order signed and ready for {symbol}: {signature}")
        return payload
