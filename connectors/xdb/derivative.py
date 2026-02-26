""" Technical implementation for Hummingbot Gateway V2.1. """

import httpx
import time
from .constants import XDB_HORIZON_URL

class XDBChainDerivative:
    def __init__(self, auth=None):
        self.auth = auth
        self.url = XDB_HORIZON_URL
        self.last_latency = 0

    async def check_network_health(self):
        """
        Tarkistaa XDB Horizon -verkon tilan.
        Ferrari-analyysi: Mitataan todellinen REST-vasteaika.
        """
        try:
            start_time = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self.url)
            
            if resp.status_code == 200:
                self.last_latency = (time.time() - start_time) * 1000
                return True
            return False
        except Exception:
            return False

    def get_metrics(self):
        """ Palauttaa diagnostiikkadatat. """
        return {
            "latency": f"{int(self.last_latency)}ms" if self.last_latency > 0 else "N/A"
        }