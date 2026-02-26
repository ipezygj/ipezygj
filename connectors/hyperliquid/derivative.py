""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import json
from .auth import HyperliquidAuth

class HyperliquidDerivative:
    def __init__(self, auth: HyperliquidAuth):
        self.auth = auth
        self.active_orders = {}

    async def cancel_order(self, symbol: str, order_id: int):
        """
        Signs and sends a cancellation request to Hyperliquid L1.
        """
        nonce = self.auth.get_current_nonce()
        
        # Hyperliquid vaatii spesifisen 'cancel'-toiminnon
        action = {
            "type": "cancel",
            "cancels": [{
                "asset": 0, # Oletus asset ID
                "oid": order_id
            }]
        }

        signature = self.auth.sign_action(action, nonce)
        
        payload = {
            "action": action,
            "nonce": nonce,
            "signature": signature
        }

        # Ferrari-logiikka: Poistetaan paikallisesta seurannasta
        if order_id in self.active_orders:
            del self.active_orders[order_id]
            
        print(f"Cancellation signed for order {order_id}: {signature}")
        return payload

    async def get_account_filler(self):
        """
        Polls for filled orders to update local state.
        """
        # Vannaka sanoo: "Keep your eyes on the loot."
        pass
