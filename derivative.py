import asyncio
import random
import time
from typing import Any, Dict, Optional
import httpx
from constants import ALPHA_EXCHANGE_PAYLOAD, STEALTH_USER_AGENTS, MIN_SPREAD_PERCENT

class TradeEngine:
    def __init__(self, name: str):
        self.name = name.upper()
        self.url = ALPHA_EXCHANGE_PAYLOAD.get(self.name)
        self.bid = 0.0
        self.ask = 0.0

    async def paivita_hinta(self, client: httpx.AsyncClient):
        headers = {"User-Agent": random.choice(STEALTH_USER_AGENTS)}
        try:
            r = await client.get(self.url, headers=headers, timeout=5.0)
            data = r.json()
            # Yksinkertaistettu hinnan poiminta (tämä vaatii pörssikohtaista hienosäätöä myöhemmin)
            # Tässä demotaan vain ideaa:
            if "BINANCE" in self.name:
                self.bid = float(data['bidPrice'])
                self.ask = float(data['askPrice'])
            elif "BYBIT" in self.name:
                self.bid = float(data['result']['list'][0]['bid1Price'])
                self.ask = float(data['result']['list'][0]['ask1Price'])
            return True
        except:
            return False

async def aja_viisasta_tutkaa():
    print("🧠 Viisas tutka käynnissä... Etsitään hintaeroja.")
    koneet = [TradeEngine(ex) for ex in ["BINANCE", "BYBIT"]] # Aloitetaan kahdella helpolla
    
    async with httpx.AsyncClient() as client:
        while True:
            await asyncio.gather(*[k.paivita_hinta(client) for k in koneet])
            
            b1, b2 = koneet[0], koneet[1]
            if b1.bid > 0 and b2.bid > 0:
                # Etsitään ero
                ero = abs(b1.bid - b2.bid)
                prosentti = (ero / min(b1.bid, b2.bid)) * 100
                
                with open("tila.txt", "w") as f:
                    f.write(f"Tarkistus: {time.strftime('%H:%M:%S')}\n")
                    f.write(f"{b1.name} Bid: {b1.bid} | {b2.name} Bid: {b2.bid}\n")
                    f.write(f"Ero: {prosentti:.4f}%\n")
                    
                    if prosentti >= MIN_SPREAD_PERCENT:
                        f.write("!!! VIISAS MAHDOLLISUUS HAVAITTU !!!\n")
                        # Tässä kohtaa 'käsityöläinen' tekisi päätöksen
            
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(aja_viisasta_tutkaa())
