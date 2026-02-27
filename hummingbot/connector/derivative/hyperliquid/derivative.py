""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import json
import websockets
from .auth import HyperliquidAuth
from .constants import WS_URL

class HyperliquidDerivative:
    def __init__(self, auth: HyperliquidAuth):
        self.auth = auth
        self.ws_url = WS_URL
        self.active_orders = {}

    async def create_order(self, symbol: str, price: float, amount: float, side: str):
        """ Creates and signs a new order for Hyperliquid L1. """
        nonce = self.auth.get_current_nonce()
        action = {
            "type": "order",
            "orders": [{
                "asset": 0,
                "isBuy": side.lower() == "buy",
                "limitPx": str(price),
                "sz": str(amount),
                "reduceOnly": False,
                "orderType": {"limit": {"tif": "Gtc"}}
            }],
            "grouping": "na"
        }
        signature = self.auth.sign_action(action, nonce)
        return {"action": action, "nonce": nonce, "signature": signature}

    async def cancel_order(self, symbol: str, order_id: int):
        """ Signs and sends a cancellation request to Hyperliquid L1. """
        nonce = self.auth.get_current_nonce()
        action = {
            "type": "cancel",
            "cancels": [{"asset": 0, "oid": order_id}]
        }
        signature = self.auth.sign_action(action, nonce)
        
        if order_id in self.active_orders:
            del self.active_orders[order_id]
            
        return {"action": action, "nonce": nonce, "signature": signature}

    async def watch_user_events(self):
        """ 
        Stealth-monitoring for order fills and balance changes.
        Automatically updates local state based on exchange events.
        """
        payload = {
            "method": "subscribe", 
            "subscription": {"type": "userEvents", "user": self.auth.address}
        }
        
        async with websockets.connect(self.ws_url) as ws:
            await ws.send(json.dumps(payload))
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                
                if data.get("type") == "userEvents":
                    events = data.get("data", {})
                    
                    # Käsitellään toteutuneet kaupat (Fills)
                    if "fills" in events:
                        for fill in events["fills"]:
                            oid = fill["oid"]
                            if oid in self.active_orders:
                                del self.active_orders[oid]
                                print(f"Stealth Sync: Order {oid} confirmed filled.")

                    # Käsitellään peruutukset (Status updates)
                    if "status" in events and events["status"] == "canceled":
                        oid = events.get("oid")
                        if oid in self.active_orders:
                            del self.active_orders[oid]
