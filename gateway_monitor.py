""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import time
import os
import sys

# TUODAAN ASETUKSET CONSTANTS-TIEDOSTOSTA
try:
    import httpx
    from termcolor import colored
    import urllib3
    import constants as c  # Nyt asetukset löytyvät c.XDB_RPC jne.
except ImportError as e:
    print(f"\n⚠️ VIRHE TUONNISSA: {e}")
    sys.exit(1)

class MasterDashboard:
    def __init__(self):
        # Käytetään constants.py tiedoston arvoja
        self.chains = {
            "HYPERLIQUID": {"url": c.HYPERLIQUID_API, "method": "POST", "payload": {"type": "meta"}, "status": "OFFLINE", "latency": "0ms"},
            "VERTEX":      {"url": c.VERTEX_GATEWAY, "method": "POST", "payload": {"type": "status"}, "status": "OFFLINE", "latency": "0ms"},
            "XDB CHAIN":   {"url": c.XDB_RPC, "method": "POST", "payload": {"jsonrpc":"2.0","method":"net_version","params":[],"id":1}, "status": "OFFLINE", "latency": "0ms"}
        }
        self.headers = {"User-Agent": c.USER_AGENT, "Content-Type": "application/json"}

    async def get_latency(self, name):
        info = self.chains[name]
        try:
            start = time.time()
            async with httpx.AsyncClient(headers=self.headers, verify=False, timeout=5.0) as client:
                if info["method"] == "POST":
                    resp = await client.post(info["url"], json=info["payload"])
                else:
                    resp = await client.get(info["url"])

                if resp.status_code < 400:
                    ms = int((time.time() - start) * 1000)
                    info["status"] = "ONLINE"
                    info["latency"] = f"{ms}ms"
                else:
                    info["status"] = f"ERR {resp.status_code}"
                    info["latency"] = "N/A"
        except Exception:
            info["status"] = "OFFLINE"
            info["latency"] = "N/A"

    def render(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        # Otsikko haetaan constantseista
        print(colored(c.DASHBOARD_TITLE, "yellow", attrs=["bold"]))
        print(colored("="*65, "grey"))
        for name, info in self.chains.items():
            s_color = "green" if info["status"] == "ONLINE" else "red"
            print(f"{colored(name.ljust(15), 'white')} | "
                  f"STATUS: {colored(info['status'].ljust(8), s_color)} | "
                  f"LATENCY: {colored(info['latency'].rjust(8), 'white')}")
        print(colored("="*65, "grey"))
        print(colored(f"Päivitetty: {time.strftime('%H:%M:%S')}", "grey"))

    async def update_loop(self):
        while True:
            for name in self.chains:
                await self.get_latency(name)
                await asyncio.sleep(0.5)
            self.render()
            await asyncio.sleep(c.UPDATE_INTERVAL)

async def main():
    db = MasterDashboard()
    await db.update_loop()

if __name__ == "__main__":
    urllib3.disable_warnings()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSammutettu.")