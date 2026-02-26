""" Technical implementation for Hummingbot Gateway V2.1. """

from .constants import PULSEX_ROUTER
from .auth import PulseXAuth

class PulseXLiquidity:
    """
    Liquidity Provision module for PulseX V2.1.
    Handles adding and removing liquidity from PulseChain pools.
    """

    def __init__(self, auth: PulseXAuth):
        self.auth = auth
        self.router_address = PULSEX_ROUTER

    async def add_liquidity(self, params: dict):
        """
        Builds a transaction for adding liquidity to a PulseX pool.
        Requires approval for both tokens in the pair.
        """
        # Logic for addLiquidityETH or addLiquidity functions
        transaction = {
            "to": self.router_address,
            "data_payload": params.get("data"),
            "value": params.get("value", 0),
        }
        return self.auth.sign_transaction(transaction)

    async def remove_liquidity(self, params: dict):
        """
        Builds a transaction for removing liquidity and receiving underlying tokens.
        """
        transaction = {
            "to": self.router_address,
            "data_payload": params.get("data"),
        }
        return self.auth.sign_transaction(transaction)
