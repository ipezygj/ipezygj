""" Technical implementation for Hummingbot Gateway V2.1 - MEGALODON CLASS """
import time, statistics, sys, getpass, json, os, datetime
from collections import deque
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

# 1. SETUP
print("🦈 FERRARI V14 - MEGALODON (MOMENTUM SNIPER)")
print("--------------------------------------------")

# Auth Load
key = ""
if os.path.exists("secrets.json"):
    try:
        with open("secrets.json") as f: key = json.load(f).get("private_key", "")
    except: pass
if not key: key = getpass.getpass("🔑 Private Key: ")
if not key.startswith("0x"): key = "0x" + key.strip()
acc = Account.from_key(key); addr = acc.address
info = Info(constants.MAINNET_API_URL, skip_ws=True)
exch = Exchange(acc, constants.MAINNET_API_URL, account_address=addr)

# 2. CONFIGURATION (HIGH PERFORMANCE)
TARGET_COINS = ["HYPE", "PURR", "AI", "PEPE", "WIF", "SOL", "JUP"]
LEVERAGE = 7       # Nostettu vipu
RISK_PCT = 0.40    # Panostetaan 40% kassasta per isku
VOL_TRIGGER = 2.5  # Vaaditaan 2.5x normaali volyymi
TRAILING_GAP = 0.008 # 0.8% Trailing Stop (Seuraa hintaa)

# Datan puskurit
candles_history = {c: deque(maxlen=25) for c in TARGET_COINS}

def log_trade(msg):
    with open("megalodon_journal.txt", "a") as f:
        f.write(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n")

print(f"🌊 HUNTING GROUNDS: {len(TARGET_COINS)} Assets")
print(f"🦈 STRATEGY: Volume Breakout + Trailing Stop | LEV: {LEVERAGE}x")

# 3. CORE LOOP
highest_price = 0
active_coin = None
entry_price = 0

while True:
    try:
        # Tsekataan ensin onko positio päällä
        state = info.user_state(addr)
        equity = float(state["marginSummary"]["accountValue"])
        positions = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]

        if positions:
            # --- RIDING THE WAVE (POSITIO AUKI) ---
            pos = positions[0]["position"]
            coin = pos["coin"]
            entry = float(pos["entryPx"])
            curr_price = float(info.all_mids()[coin])
            roi = (curr_price - entry) / entry if float(pos["szi"]) > 0 else (entry - curr_price) / entry
            
            # Trailing Stop Logiikka
            if active_coin != coin: # Jos botti käynnistettiin kesken kaupan
                active_coin = coin
                highest_price = curr_price
                entry_price = entry

            if curr_price > highest_price:
                highest_price = curr_price # Uusi huippu! Stop Loss nousee.
            
            # Lasketaan dynaaminen stop loss
            stop_price = highest_price * (1 - TRAILING_GAP)
            
            print(f"🏄 RIDING {coin} | ROI: {roi*100:+.2f}% | Price: {curr_price:.4f} | Stop: {stop_price:.4f} | Peak: {highest_price:.4f}")

            # Exit ehto: Hinta putoaa huipusta Trailing Gapin verran
            if curr_price < stop_price:
                print(f"💰 BANKING PROFIT! {coin} hit Trailing Stop.")
                exch.market_close(coin)
                log_trade(f"EXIT {coin} | ROI: {roi*100:.2f}% | Equity: ${equity:.2f}")
                active_coin = None
                highest_price = 0
                time.sleep(5)

        else:
            # --- HUNTING MODE (ETSI VALAS) ---
            print(f"📡 SCANNING... Eq: ${equity:.2f} | Waiting for Vol Surge...", end="\r")
            
            for coin in TARGET_COINS:
                # Haetaan nopeasti viimeisin 1min kynttilä
                c = info.candles_snapshot(coin, "1m", 25, datetime.datetime.now())
                if not c: continue
                
                last_vol = float(c[-1]['v'])
                last_close = float(c[-1]['c'])
                prev_close = float(c[-2]['c'])
                
                # Laske keskiarvovolyymi (viimeiset 20 min)
                avg_vol = sum(float(x['v']) for x in c[-21:-1]) / 20
                if avg_vol == 0: continue
                
                vol_ratio = last_vol / avg_vol
                price_change = (last_close - prev_close) / prev_close

                # TRIGGER: Volyymi räjähtää JA hinta nousee (ei laske)
                if vol_ratio > VOL_TRIGGER and price_change > 0.0015: # +0.15% nousu minuutissa
                    print(f"\n🚀 LAUNCH! {coin} Vol: {vol_ratio:.1f}x | Price Up!")
                    
                    # Laske positio
                    size = round(((equity * RISK_PCT) * LEVERAGE) / last_close, 1)
                    if size > 0:
                        print(f"🦈 MEGALODON BITE: {coin} @ {last_close}")
                        exch.market_open(coin, True, size, last_close, 0.01)
                        log_trade(f"ENTRY {coin} | VolRatio: {vol_ratio:.1f}x")
                        active_coin = coin
                        highest_price = last_close
                        time.sleep(2)
                        break

        time.sleep(2) # 2 sekunnin sykli

    except Exception as e:
        print(f"⚠️ Error: {e}"); time.sleep(5)
