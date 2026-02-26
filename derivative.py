import asyncio
import random
import time
from typing import Any, Dict, Optional
import httpx
from constants import ALPHA_EXCHANGE_PAYLOAD, STEALTH_USER_AGENTS, ADAPTIVE_JITTER_MS

class GatewayConnector:
    def __init__(self, name: str):
        self.name = name.upper()
        self.url = ALPHA_EXCHANGE_PAYLOAD.get(self.name)
        self.viimeisin_viive = 0

    async def hae(self, client: httpx.AsyncClient):
        # Adaptive Jitter takaisin konepeltiin
        await asyncio.sleep(random.randint(*ADAPTIVE_JITTER_MS) / 1000.0)
        
        headers = {"User-Agent": random.choice(STEALTH_USER_AGENTS)}
        alku = time.time()
        try:
            r = await client.get(self.url, headers=headers, timeout=5.0)
            self.viimeisin_viive = int((time.time() - alku) * 1000)
            with open("lokit.txt", "a") as f:
                f.write(f"{time.strftime('%H:%M:%S')} - {self.name}: {self.viimeisin_viive}ms\n")
            return True
        except:
            self.viimeisin_viive = -1 # Merkataan virhe
            return False

async def aja():
    # Connection Pooling takaisin käyttöön (httpx oletusasetukset ovat hyvät, mutta käytetään yhtä clientia)
    print("Botti käynnissä... Katso tilanne: cat tila.txt")
    
    koneet = [GatewayConnector(ex) for ex in ALPHA_EXCHANGE_PAYLOAD.keys()]
    
    async with httpx.AsyncClient(limits=httpx.Limits(max_connections=100, max_keepalive_connections=20)) as client:
        while True:
            await asyncio.gather(*[k.hae(client) for k in koneet])
            
            # Kirjoitetaan nopea tilannekatsaus "mittaristoon"
            with open("tila.txt", "w") as f:
                f.write(f"Päivitetty: {time.strftime('%H:%M:%S')}\n")
                for k in koneet:
                    status = f"{k.viimeisin_viive}ms" if k.viimeisin_viive > 0 else "VIRHE"
                    f.write(f"{k.name}: {status}\n")
            
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(aja())
    except KeyboardInterrupt:
        print("\nLopetettu.")
