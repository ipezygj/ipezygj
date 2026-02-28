""" Technical implementation for Hummingbot Gateway V2.1. """
import hashlib
import hmac
import time
from typing import Any, Dict

from .constants import VERTEX_REST_URL


class StealthAuthenticator:
    """
    Handles secure L2 cryptographic signing for V2.1 Gateway.
    Keeps private keys entirely in-memory during execution.
    """

    def __init__(self, api_key: str, api_secret: str):
        self._api_key = api_key
        self._api_secret = api_secret

    def generate_signature(self, payload: str) -> str:
        """ Generates HMAC SHA256 signature with absolute stealth precision. """
        return hmac.new(self._api_secret.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()
        
    def get_auth_headers(self) -> Dict[str, Any]:
        """ Constructs headers without leaking core secrets. """
        timestamp = str(int(time.time() * 1000))
        signature = self.generate_signature(timestamp)
        return {
            "X-API-KEY": self._api_key,
            "X-TIMESTAMP": timestamp,
            "X-SIGNATURE": signature
        }
