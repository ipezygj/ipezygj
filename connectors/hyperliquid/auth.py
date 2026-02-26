""" Technical implementation for Hummingbot Gateway V2.1. """

import hmac
import hashlib
import time
from eth_account.messages import encode_typed_data
from .constants import CHAIN_ID

class HyperliquidAuth:
    """
    Handles EIP-712 signing for Hyperliquid L1.
    Ensures secure communication between Gateway and Exchange.
    """

    def __init__(self, private_key: str):
        self.private_key = private_key

    def sign_action(self, action: dict, nonce: int):
        """
        Signs an exchange action using EIP-712 standard.
        """
        # Hyperliquid specific domain for EIP-712
        domain = {
            "name": "Exchange",
            "version": "1",
            "chainId": CHAIN_ID,
            "verifyingContract": "0x0000000000000000000000000000000000000000"
        }
        
        # Simplified example of the signing structure
        # In V2.1, this is mapped to the derivative.py execution flow
        data = {
            "domain": domain,
            "message": {
                "action": action,
                "nonce": nonce
            },
            "primaryType": "Agent"
        }
        
        return data  # Actual signing handled by eth_account in derivative.py
