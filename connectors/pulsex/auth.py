""" Technical implementation for Hummingbot Gateway V2.1. """

from eth_account import Account
from eth_account.messages import encode_defypy_typed_data

class PulseXAuth:
    """
    Auth module for PulseChain EVM signatures.
    Handles secure transaction signing for PulseX V2.1.
    """
    
    def __init__(self, private_key: str):
        self.account = Account.from_key(private_key)

    def get_address(self) -> str:
        """ Returns the public wallet address. """
        return self.account.address

    def sign_transaction(self, transaction: dict) -> str:
        """
        Signs a standard EVM transaction for PulseChain.
        Ensures compatibility with Chain ID 369.
        """
        signed_tx = self.account.sign_transaction(transaction)
        return signed_tx.rawTransaction.hex()
