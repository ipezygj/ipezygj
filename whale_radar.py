import time, datetime, sys
from hyperliquid.info import Info
from hyperliquid.utils import constants

# KONFIGURAATIO
TARGETS = ["HYPE", "PURR", "AI", "PEPE", "WIF", "SOL", "JUP", "TIA", "SUI", "ARB", "ETH"]
TIMEFRAME = "15m"  # Katsotaan 15min kynttilöitä
VOL_THRESHOLD = 3.0  # Hälytys, jos volyymi on 3x normaalia suurempi

print("🦈 FERRARI WHALE RADAR ACTIVE")
print(f"📡 Scanning {len(TARGETS)} assets for volume spikes > {VOL_THRESHOLD}x")
print("----------------------------------------------------")

info = Info(constants.MAINNET_API_URL, skip_ws=True)

def check_whales():
    alerts = []
    print(f"\n🕒 SCAN TIME: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    for coin in TARGETS:
        try:
            # Haetaan viimeiset kynttilät
            candles = info.candles_snapshot(coin, TIMEFRAME, 1000, datetime.datetime.now())
            if not candles or len(candles) < 20: continue

            # Data: Uusin kynttilä vs. Keskiarvo
            last_candle = candles[-1]
            last_vol = float(last_candle['v'])
            last_close = float(last_candle['c'])
            
            # Lasketaan edellisten 20 kynttilän keskimääräinen volyymi
            avg_vol = sum(float(c['v']) for c in candles[-22:-2]) / 20
            
            if avg_vol == 0: continue
            
            ratio = last_vol / avg_vol
            
            # Visuaalinen palkki
            bars = "█" * int(ratio) if ratio < 10 else "██████████+"
            
            if ratio > VOL_THRESHOLD:
                print(f"🚨 WHALE DETECTED: {coin:4} | Vol: {ratio:.1f}x AVG | Price: ${last_close:.4f}")
                alerts.append(coin)
            elif ratio > 1.5:
                print(f"🌊 Swell building: {coin:4} | Vol: {ratio:.1f}x AVG | {bars}")
            
        except Exception as e:
            continue
            
    if not alerts:
        print("💤 No active whales. Ocean is calm.")
    else:
        print(f"🔥 ACTION REQUIRED: {', '.join(alerts)}")

while True:
    try:
        check_whales()
        time.sleep(30) # Skannaus 30s välein
    except KeyboardInterrupt:
        print("\n🦈 Radar OFF")
        sys.exit()
    except Exception as e:
        print(f"⚠️ Error: {e}")
        time.sleep(10)
