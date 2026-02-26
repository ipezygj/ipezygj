""" Technical implementation for Hummingbot Gateway V2.1. """
import asyncio
import time
import httpx
import urllib3
from termcolor import colored
from stellar_sdk import Keypair

from constants import ALPHA_EXCHANGE_PAYLOAD, STEALTH_HEADERS, NETWORK_TIMEOUT_GLOBAL

try:
    PUB_KEY = Keypair.random().public_key
except:
    PUB_KEY = "GAQQGFSLILQCPSAVP4B6SKT6XBQDXQZFGZJFNTB46ZJ3Z77QJIFKSBBJ"

class StealthEngine:
    def __init__(self):
        self.results = {name: "PENDING" for name in ALPHA_EXCHANGE_PAYLOAD}

    async def fetch_latency(self, client, name, url):
        start = time.time()
        try:
            await client.get(url, headers=STEALTH_HEADERS, timeout=NETWORK_TIMEOUT_GLOBAL)
            self.results[name] = f"{int((time.time() - start) * 1000)}ms"
        except Exception:
            self.results[name] = "ERR/TMO"

    async def check_all(self):
        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_latency(client, name, url) for name, url in ALPHA_EXCHANGE_PAYLOAD.items()]
            await asyncio.gather(*tasks)

    def render(self):
        print("\033[H\033[J", end="")
        print(colored("STEALTH MASTER DASHBOARD V2.1 [MODULAR ARCHITECTURE] 🏎️", "cyan", attrs=["bold"]))
        print("======================================================================")
        names = sorted(list(ALPHA_EXCHANGE_PAYLOAD.keys()))
        for i in range(0, len(names), 2):
            n1 = names[i]
            r1 = self.results[n1]
            str1 = f"{n1:12} | LATENCY: {r1:7}"
            if i+1 < len(names):
                n2 = names[i+1]
                r2 = self.results[n2]
                str2 = f"{n2:12} | LATENCY: {r2:7}"
            else:
                str2 = ""
            print(colored(f"{str1:34} {str2}", "green" if "ms" in r1 else "yellow"))
        print("======================================================================")
        print(colored(f"XDB Wallet: {PUB_KEY}", "cyan"))
        print(colored(f"Updated: {time.strftime('%H:%M:%S')} | Press Ctrl+C to stop", "grey"))

    async def loop(self):
        while True:
            await self.check_all()
            self.render()
            await asyncio.sleep(5)

if __name__ == "__main__":
    urllib3.disable_warnings()
    try:
        asyncio.run(StealthEngine().loop())
    except KeyboardInterrupt:
        pass
