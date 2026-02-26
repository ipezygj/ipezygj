# Technical implementation for Hummingbot Gateway V2.1.
import eth_account
from eth_account.messages import encode_typed_data
from .constants import ARBITRUM_CHAIN_ID

class VertexAuth:
    def __init__(self, private_key: str):
        self.account = eth_account.Account.from_key(private_key)
        self.address = self.account.address
        self.chain_id = ARBITRUM_CHAIN_ID

    def sign_order(self, order_params: dict):
        """
        Signs a Vertex order using EIP-712.
        Vannaka says: "A signature is a promise written in code."
        """
        # Vertex vaatii spesifisen domain-rakenteen
        domain = {
            "name": "Vertex",
            "version": "0.1.0",
            "chainId": self.chain_id,
            "verifyingContract": "0x..." # Lisätään virallinen sopimusosoite
        }
        
        # Rakennetaan EIP-712-standardin mukainen viesti
        message = {
            "sender": self.address,
            "priceX18": str(order_params['price']),
            "amount": str(order_params['amount']),
            "expiration": int(order_params['expiration']),
            "nonce": int(order_params['nonce'])
        }
        
        # Allekirjoitetaan data
        signable_msg = encode_typed_data(domain_data=domain, message_types={"Order": message}, message_data=message)
        signed_msg = self.account.sign_message(signable_msg)
        
        return signed_msg.signature.hex()
