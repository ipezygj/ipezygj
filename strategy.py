""" Technical implementation for Hummingbot Gateway V2.1. """
import asyncio
import sqlite3
import os
import httpx
from datetime import datetime

LOG_FILE = os.path.expanduser('~/my_ferrari/strategy.log')
DB_FILE = os.path.expanduser('~/my_ferrari/strategy.db')

# Asset IDs: ETH, BTC, ARB
PYTH_IDS = [
    "ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace",
    "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
    "3fa4252848f9f0a1480be62745a4629d9eb1322aebab8a791e344b3b9c1adcf5"
]
IDS_PARAM = "&".join([f"ids[]={i}" for i in PYTH_IDS])
PYTH_URL = f"https://hermes.pyth.network/v2/updates/price/latest?{IDS_PARAM}"

ASSET_MAP = {
    "ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace": "ETH/USD",
    "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43": "BTC/USD",
    "3fa4252848f9f0a1480be62745a4629d9eb1322aebab8a791e344b3b9c1adcf5": "ARB/USD"
}

async def fetch_pyth_prices(client):
    try:
        response = await client.get(PYTH_URL, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data['parsed']:
            asset_id = item['id']
            pair_name = ASSET_MAP.get(asset_id, "UNKNOWN")
            price_data = item['price']
            price = int(price_data['price']) * (10 ** int(price_data['expo']))
            results.append((pair_name, price))
        return results
    except Exception as e:
        print(f"⚠️ Pyth Fetch Error: {e}")
        return []

def save_to_db(prices):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        for pair, price in prices:
            c.execute("INSERT INTO prices (pair, price) VALUES (?, ?)", (pair, price))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ DB Error: {e}")

async def track_market():
    print("🏎️ THE SIGNAL FOUNDRY ELITE - V12 MULTI-ASSET ACTIVE")
    async with httpx.AsyncClient() as client:
        while True:
            prices = await fetch_pyth_prices(client)
            ts = datetime.now().isoformat()
            
            if prices:
                log_str = " | ".join([f"{p[0]}: ${p[1]:.4f}" for p in prices])
                print(f"[{ts}] 🔮 {log_str}")
                save_to_db(prices)
            else:
                print(f"[{ts}] 📉 Market intel lost, retrying next cycle...")
            
            await asyncio.sleep(300)

if __name__ == "__main__":
    try:
        asyncio.run(track_market())
    except KeyboardInterrupt:
        print("\n🏁 Ferrari returned to garage.")
