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
        # Pidetään matalaa profiilia
        await asyncio.sleep(random.randint(*ADAPTIVE_JITTER_MS) / 1000.0)
        
        headers = {"User-Agent": random.choice(STEALTH_USER_AGENTS)}
        alku = time.time()
        try:
            r = await client.get(self.url, headers=headers, timeout=5.0)
            self.viimeisin_viive = int((time.time() - alku) * 1000)
            return True
        except:
            self.viimeisin_viive = -1
            return False

async def aja():
    print("Värkätään... seurataan tilannetta tila.txt tiedostosta.")
    koneet = [GatewayConnector(ex) for ex in ALPHA_EXCHANGE_PAYLOAD.keys()]
    
    while True:
        try:
            # Luodaan yhteyspankki tässä, jotta se pysyy tuoreena
            limits = httpx.Limits(max_connections=50, max_keepalive_connections=10)
            async with httpx.AsyncClient(limits=limits) as client:
                for _ in range(100): # Tehdään sata kierrosta kerrallaan
                    await asyncio.gather(*[k.hae(client) for k in koneet])
                    
                    with open("tila.txt", "w") as f:
                        f.write(f"Päivitetty: {time.strftime('%H:%M:%S')}\n")
                        for k in koneet:
                            status = f"{k.viimeisin_viive}ms" if k.viimeisin_viive > 0 else "---"
                            f.write(f"{k.name:12}: {status}\n")
                    
                    await asyncio.sleep(8) # Rauhallinen tahti
        except Exception:
            # Jos tulee jokin isompi solmu, levätään hetki ja yritetään uusiksi
            await asyncio.sleep(30)
            continue

if __name__ == "__main__":
    try:
        asyncio.run(aja())
    except KeyboardInterrupt:
        print("\nLopetettu tältä erää.")
