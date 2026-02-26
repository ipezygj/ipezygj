""" Technical implementation for Hummingbot Gateway V2.1. """

from eth_account import Account

class XDBAuth:
    """
    Standardized Auth for XDB Chain.
    Designed for Hummingbot Gateway V2.1.
    """
    def __init__(self, private_key: str):
        self.account = Account.from_key(private_key)
        self.address = self.account.address

    def sign_transaction(self, transaction: dict):
        """
        Signs an XDB Chain transaction payload.
        Vannaka says: "A sharp blade needs a steady hand."
        """
        # XDB Chain on EVM-pohjainen, joten käytetään standardia allekirjoitusta
        signed_txn = Account.sign_transaction(transaction, self.account.key)
        return signed_txn.rawTransaction.hex()

    def get_address(self):
        return self.address
