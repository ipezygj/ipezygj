""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import time
import os
import httpx
from termcolor import colored
import urllib3
# Ferrari-analyysi: Tuodaan uusi XDB-natiivi Auth
from stellar_sdk import Keypair

# --- KONFIGURAATIO ---
XDB_HORIZON = "https://horizon.livenet.xdbchain.com/"
HYPERLIQUID_API = "https://api.hyperliquid.xyz/info"
UPDATE_INTERVAL = 3.0

class StealthEngine:
    def __init__(self):
        self.url_xdb = XDB_HORIZON
        self.url_hl = HYPERLIQUID_API
        self.xdb_status = "OFFLINE"
        self.xdb_latency = "N/A"
        self.hl_status = "OFFLINE"
        self.hl_latency = "N/A"
        
        # Luodaan XDB-natiivi avainpari monitorointia varten
        # Huom: Tämä luo uuden osoitteen joka kerta, kunnes tallennamme seedin
        self.kp = Keypair.random()
        self.xdb_address = self.kp.public_key

    async def check_xdb(self):
        try:
            start = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(self.url_xdb)
            if resp.status_code == 200:
                self.xdb_latency = f"{int((time.time() - start) * 1000)}ms"
                self.xdb_status = "ONLINE"
                return True
            return False
        except Exception:
            self.xdb_status = "OFFLINE"
            return False

    async def check_hl(self):
        try:
            start = time.time()
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(self.url_hl, json={"type": "meta"})
            if resp.status_code == 200:
                self.hl_latency = f"{int((time.time() - start) * 1000)}ms"
                self.hl_status = "ONLINE"
                return True
            return False
        except Exception:
            self.hl_status = "OFFLINE"
            return False

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(colored("🏎️  STEALTH MASTER DASHBOARD V2.1 [XDB NATIVE] 🏎️", "yellow", attrs=["bold"]))
        print(colored("="*70, "grey"))
        
        hl_color = "green" if self.hl_status == "ONLINE" else "red"
        print(f"{'HYPERLIQUID'.ljust(15)} | STATUS: {colored(self.hl_status.ljust(8), hl_color)} | LATENCY: {str(self.hl_latency).rjust(8)}")
        
        xdb_color = "green" if self.xdb_status == "ONLINE" else "red"
        print(f"{'XDB CHAIN'.ljust(15)} | STATUS: {colored(self.xdb_status.ljust(8), xdb_color)} | LATENCY: {str(self.xdb_latency).rjust(8)}")
        
        print(colored("="*70, "grey"))
        print(colored(f"XDB Wallet (Native G-Addr): {self.xdb_address}", "cyan"))
        print(colored(f"Päivitetty: {time.strftime('%H:%M:%S')}", "grey"))

    async def loop(self):
        while True:
            await asyncio.gather(self.check_xdb(), self.check_hl())
            self.render()
            await asyncio.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    urllib3.disable_warnings()
    engine = StealthEngine()
    try:
        asyncio.run(engine.loop())
    except KeyboardInterrupt:
        print("\nSammutettu.")