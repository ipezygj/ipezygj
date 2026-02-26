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

    async def hae(self, client: httpx.AsyncClient, porrastus: float):
        # 16. Turbo: Porrastettu lähtöruutu + satunnainen jitter
        await asyncio.sleep(porrastus + (random.randint(*ADAPTIVE_JITTER_MS) / 1000.0))
        
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
    print("Turbo 16 aktivoitu... Porrastettu haku käynnissä.")
    koneet = [GatewayConnector(ex) for ex in ALPHA_EXCHANGE_PAYLOAD.keys()]
    
    # Lasketaan pieni porrastusväli (esim. 0.1s välein per pörssi)
    stagger_step = 0.1 

    while True:
        try:
            limits = httpx.Limits(max_connections=50, max_keepalive_connections=10)
            async with httpx.AsyncClient(limits=limits) as client:
                for _ in range(50):
                    # Lähetetään haut porrastetusti
                    tasks = []
                    for i, k in enumerate(koneet):
                        tasks.append(k.hae(client, i * stagger_step))
                    
                    await asyncio.gather(*tasks)
                    
                    with open("tila.txt", "w") as f:
                        f.write(f"Päivitetty: {time.strftime('%H:%M:%S')} | Turbo 16: Active\n")
                        f.write("-" * 40 + "\n")
                        # Järjestetään nopeuden mukaan, niin nähdään kuka johtaa
                        aktiiviset = sorted(koneet, key=lambda x: (x.viimeisin_viive <= 0, x.viimeisin_viive))
                        for k in aktiiviset:
                            status = f"{k.viimeisin_viive}ms" if k.viimeisin_viive > 0 else "---"
                            f.write(f"{k.name:15}: {status}\n")
                    
                    await asyncio.sleep(5) # Hieman tiheämpi tahti, kun on tehoja
        except Exception:
            await asyncio.sleep(10)
            continue

if __name__ == "__main__":
    try:
        asyncio.run(aja())
    except KeyboardInterrupt:
        print("\nVarikko lukittu.")
