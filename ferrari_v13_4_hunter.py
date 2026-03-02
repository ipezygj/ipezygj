""" Technical implementation for Hummingbot Gateway V2.1. """
import time, statistics, sys, getpass, json, os, datetime, random
from collections import deque
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

# 1. SETUP
print("🕵️ FERRARI V13.4.3 - AGGRESSIVE HUNTER ACTIVE")
print("---------------------------------------------")
key = ""
if os.path.exists("secrets.json"):
    try:
        with open("secrets.json") as f:
            key = json.load(f).get("private_key", "")
    except: pass
if not key: key = getpass.getpass("🔑 Private Key: ")

try:
    if not key.startswith("0x"): key = "0x" + key.strip()
    acc = Account.from_key(key); addr = acc.address
except: print("❌ Auth Fail"); sys.exit()

info = Info(constants.MAINNET_API_URL, skip_ws=True)
exch = Exchange(acc, constants.MAINNET_API_URL, account_address=addr)

# 2. CONFIGURATION - HERKEMMÄT SÄÄDÖT
TARGET_COINS = ["HYPE", "ARB", "PURR", "AI", "PEPE", "WIF", "SOL", "JUP", "TIA", "SUI"]
LEVERAGE = 4
RISK_PCT = 0.35
# Z-TRIGGER laskettu -2.85 -> -2.2 (Lisää iskuja!)
Z_TRIGGER = -2.2
histories = {coin: deque(maxlen=60) for coin in TARGET_COINS}

def log_event(msg):
    with open("profits.txt", "a") as f:
        t = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{t}] {msg}\n")

while True:
    try:
        mids = info.all_mids()
        state = info.user_state(addr)
        equity = float(state["marginSummary"]["accountValue"])
        
        active_pos = None
        for p in state["assetPositions"]:
            if abs(float(p["position"]["szi"])) > 0:
                active_pos = p["position"]
                break
        
        if active_pos:
            # --- BATTLE MODE X-RAY ---
            coin = active_pos["coin"]
            sz = float(active_pos["szi"]); entry = float(active_pos["entryPx"])
            curr = float(mids[coin])
            roi = (curr - entry) / entry if sz > 0 else (entry - curr) / entry
            
            l2 = info.l2_snapshot(coin)
            bids = sum(float(b['sz']) for b in l2['levels'][0][:3])
            asks = sum(float(a['sz']) for a in l2['levels'][1][:3])
            imb = bids / asks if asks > 0 else 1.0
            
            print(f"⚔️ BATTLE: {coin:4} | ROI: {roi*100:+.2f}% | Imb: {imb:.1f} | Eq: ${equity:.2f}")
            
            if roi > 0.006: # Sniper Exit hieman aikaisemmin
                exch.market_close(coin)
                log_event(f"WIN {coin}: {roi*100:.2f}%")
                time.sleep(10)
            elif roi < -0.025:
                exch.market_close(coin)
                log_event(f"LOSS {coin}: {roi*100:.2f}%")
                time.sleep(10)
        else:
            # --- MULTI-SCAN AGGRESSIVE ---
            best_coin = None
            for coin in TARGET_COINS:
                if coin not in mids: continue
                px = float(mids[coin])
                histories[coin].append(px)
                
                if len(histories[coin]) > 15: # Nopeutettu historian kertymistä
                    avg = sum(histories[coin]) / len(histories[coin])
                    std = statistics.stdev(histories[coin])
                    z = (px - avg) / std if std > 0 else 0
                    
                    if z < Z_TRIGGER:
                        best_coin = coin
                        break
            
            # HUD-päivitys joka syklillä
            status = f"📡 SCANNING {len(TARGET_COINS)} | Eq: ${equity:.2f} | Z-Trigger: {Z_TRIGGER}"
            print(status, end="\r")

            if best_coin:
                price = float(mids[best_coin])
                size = round(((equity * RISK_PCT) * LEVERAGE) / price, 1)
                if size > 0:
                    print(f"\n⚡ ATTACK: {best_coin} Z-Score: {z:.2f}")
                    exch.market_open(best_coin, True, size, price, 0.01)
                    log_event(f"ENTRY {best_coin} Z:{z:.2f}")
                    time.sleep(5)

        time.sleep(1.2)

    except Exception as e:
        print(f"\n⚠️ Error: {e}"); time.sleep(5)
