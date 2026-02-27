""" Technical implementation for Strategy Engine V3.2 - Stealth Cooldown. """
import asyncio
import time

import httpx

from imbalance_engine import calculate_imbalance
from signal_foundry import SignalFoundry


SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
persistence_db = {s: [] for s in SYMBOLS} 
cooldowns = {s: 0.0 for s in SYMBOLS} # 🧊 KÄSITYÖLÄISEN JÄÄHDYTIN

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
    print("🏎️💨 STEALTH MODE ENGAGED: Silent Hunter active (3/3 checks, 70% threshold, 5min Cooldown)...")
    foundry = SignalFoundry(initial_capital=200.0)
    cooldown_time = 300 # 🧊 300 sekuntia = 5 minuutin jäähy signaalin jälkeen
    
    async with httpx.AsyncClient() as client:
        while True:
            current_time = time.time()
            
            for symbol in SYMBOLS:
                # 🧊 Jos kolikko on vielä jäähyllä, ohitetaan skannaus
                if current_time - cooldowns[symbol] < cooldown_time:
                    continue
                    
                price, strength = await get_full_market_pressure(client, symbol)
                
                if price > 0:
                    persistence_db[symbol].append(strength)
                    if len(persistence_db[symbol]) > 3:
                        persistence_db[symbol].pop(0)
                    
                    if len(persistence_db[symbol]) == 3:
                        avg_strength = sum(persistence_db[symbol]) / 3
                        
                        # Varmistetaan että paine ei heilahtele edestakaisin
                        all_same_dir = all((s > 0 if avg_strength > 0 else s < 0) for s in persistence_db[symbol])
                        
                        if abs(avg_strength) > 0.70 and all_same_dir:
                            direction = "📈 BUY PRESSURE" if avg_strength > 0 else "📉 SELL PRESSURE"
                            signal = {
                                "asset": symbol, "stable": True, "price": price,
                                "custom_msg": f"🛰️ *STEALTH STRIKE ALERT*\n{direction}\n🔥 *Verified Strength:* {abs(avg_strength)*100:.1f}%\n⏱️ *Stability:* 3/3 Checks"
                            }
                            await foundry.broadcast_signal(signal)
                            
                            # 🧊 Ammuttiin signaali -> Laitetaan jäähy päälle ja nollataan putki
                            cooldowns[symbol] = current_time 
                            persistence_db[symbol] = [] 
                            print(f"🤫 [STEALTH] Alpha iski kohteeseen {symbol}. Ase lukittu 5 minuutiksi.")
                
            await asyncio.sleep(1.0) # Käsityöläisen vakaa, rauhallinen rytmi
