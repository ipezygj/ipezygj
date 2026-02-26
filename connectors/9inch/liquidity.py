""" Technical implementation for Hummingbot Gateway V2.1. """

from .constants import NINE_INCH_ROUTER
from .auth import NineInchAuth

class NineInchLiquidity:
    """
    Liquidity Provision module for 9inch V2.1.
    Automates adding and removing liquidity for community tokens.
    """

    def __init__(self, auth: NineInchAuth):
        self.auth = auth
        self.router_address = NINE_INCH_ROUTER

    async def add_liquidity(self, params: dict):
        """
        Builds a transaction for adding liquidity to a 9inch pool.
        """
        transaction = {
            "to": self.router_address,
            "data_payload": params.get("data"),
            "value": params.get("value", 0),
        }
        return self.auth.sign_transaction(transaction)

    async def remove_liquidity(self, params: dict):
        """
        Builds a transaction for removing liquidity.
        """
        transaction = {
            "to": self.router_address,
            "data_payload": params.get("data"),
        }
        return self.auth.sign_transaction(transaction)
