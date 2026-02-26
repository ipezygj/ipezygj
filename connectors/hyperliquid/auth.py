""" Technical implementation for Hummingbot Gateway V2.1. """

import time
from eth_account import Account
from eth_account.messages import encode_typed_data

class HyperliquidAuth:
    """
    Standardized EIP-712 Auth for Hyperliquid.
    Designed for Hummingbot Gateway V2.1.
    """
    def __init__(self, private_key: str):
        self.account = Account.from_key(private_key)
        self.address = self.account.address

    def sign_action(self, action: dict, nonce: int):
        """
        Signs a trading action using EIP-712.
        """
        # Hyperliquid-spesifinen domain-rakenne
        domain = {
            "name": "Exchange",
            "version": "1",
            "chainId": 1337,  # Hyperliquid L1 sisäinen ID
            "verifyingContract": "0x0000000000000000000000000000000000000000"
        }

        # Tämä on se "taika", joka tekee kaupankäynnistä mahdollista
        data = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"}
                ],
                "Agent": [
                    {"name": "source", "type": "string"},
                    {"name": "connectionId", "type": "bytes32"}
                ]
            },
            "primaryType": "Agent",
            "domain": domain,
            "message": action
        }

        signed = self.account.sign_message(encode_typed_data(full_message=data))
        return signed.signature.hex()

    def get_current_nonce(self):
        """ Returns millisecond timestamp for nonce. """
        return int(time.time() * 1000)
