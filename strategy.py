""" Technical implementation for Strategy Engine V3.2 - Stealth Hunter. """
import asyncio
import httpx
from signal_foundry import SignalFoundry
from imbalance_engine import calculate_imbalance

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
persistence_db = {s: [] for s in SYMBOLS} 

async def get_full_market_pressure(client, symbol):
    try:
        url = f"https://api.binance.com/api/v3/depth?symbol={symbol}&limit=20"
        r = await client.get(url, timeout=5.0)
        data = r.json()
        strength = calculate_imbalance(data['bids'], data['asks'], depth=10)
        price = float(data['bids'][0][0])
        return price, strength
    except Exception:
        return 0, 0

async def run_alpha_strategy():
    print("🏎️💨 STEALTH MODE ENGAGED: Silent Hunter active (3/3 checks, 70% threshold)...")
    foundry = SignalFoundry(initial_capital=200.0)
    
    async with httpx.AsyncClient() as client:
        while True:
            for symbol in SYMBOLS:
                price, strength = await get_full_market_pressure(client, symbol)
                
                if price > 0:
                    persistence_db[symbol].append(strength)
                    if len(persistence_db[symbol]) > 3:
                        persistence_db[symbol].pop(0)
                    
                    if len(persistence_db[symbol]) == 3:
                        avg_strength = sum(persistence_db[symbol]) / 3
                        
                        # Syvä Ferrari-analyysi: Varmistetaan että paine ei heilahtele edestakaisin
                        all_same_dir = all((s > 0 if avg_strength > 0 else s < 0) for s in persistence_db[symbol])
                        
                        if abs(avg_strength) > 0.70 and all_same_dir:
                            direction = "📈 BUY PRESSURE" if avg_strength > 0 else "📉 SELL PRESSURE"
                            signal = {
                                "asset": symbol, "stable": True, "price": price,
                                "custom_msg": f"🛰️ *STEALTH STRIKE ALERT*\n{direction}\n🔥 *Verified Strength:* {abs(avg_strength)*100:.1f}%\n⏱️ *Stability:* 3/3 Checks"
                            }
                            await foundry.broadcast_signal(signal)
                            persistence_db[symbol] = [] # Nollataan osuman jälkeen, jotta ei spämmää
                
                await asyncio.sleep(1.0) # Käsityöläisen vakaa, rauhallinen rytmi
