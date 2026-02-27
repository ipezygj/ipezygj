""" Technical implementation for Hummingbot Gateway V2.1. """
import asyncio
import sqlite3
import os
import httpx
from datetime import datetime

# Stealth configuration
LOG_FILE = os.path.expanduser('~/my_ferrari/strategy.log')
DB_FILE = os.path.expanduser('~/my_ferrari/strategy.db')
PYTH_ETH_USD_ID = "ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"
PYTH_URL = f"https://hermes.pyth.network/v2/updates/price/latest?ids[]={PYTH_ETH_USD_ID}"

async def fetch_pyth_price(client):
    try:
        response = await client.get(PYTH_URL, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        
        # Pyth palauttaa hinnan ja eksponentin
        price_data = data['parsed'][0]['price']
        price = int(price_data['price'])
        expo = int(price_data['expo'])
        
        # Lasketaan todellinen hinta (esim. hinta * 10^-8)
        actual_price = price * (10 ** expo)
        return actual_price
    except Exception as e:
        print(f"⚠️ Pyth Fetch Error: {e}")
        return None

def save_to_db(price):
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO prices (pair, price) VALUES (?, ?)", ('ETH/USD', price))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"❌ DB Error: {e}")

async def track_market():
    print("🏎️ THE SIGNAL FOUNDRY ELITE - LIVE MARKET ACTIVE")
    
    async with httpx.AsyncClient() as client:
        while True:
            price = await fetch_pyth_price(client)
            ts = datetime.now().isoformat()
            
            if price:
                print(f"[{ts}] 🔮 Pyth ETH/USD: ${price:.2f}")
                save_to_db(price)
            else:
                print(f"[{ts}] 📉 Market intel lost, retrying next cycle...")
            
            # Odotetaan 5 minuuttia
            await asyncio.sleep(300)

if __name__ == "__main__":
    try:
        asyncio.run(track_market())
    except KeyboardInterrupt:
        print("\n🏁 Ferrari returned to garage.")
