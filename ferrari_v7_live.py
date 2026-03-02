""" Technical implementation for Hummingbot Gateway V2.1. """
import time, statistics, sys, getpass, json, os, datetime, random
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

# 1. SNIPER SETUP
print("🎯 FERRARI V13.1 - SNIPER EXIT EDITION")
print("---------------------------------------")
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

# 2. CONSTANTS
COIN = "HYPE"
LEVERAGE = 4
RISK_PCT = 0.35
hist = []
hwm, last_trade_time = 0, 0

def log_event(msg):
    with open("profits.txt", "a") as f:
        t = datetime.datetime.now().strftime("%H:%M:%S")
        f.write(f"[{t}] {msg}\n")

print(f"🏁 SNIPER ACTIVE | LOCK-IN PROFIT: ON | SPOOF-FILTER: ON")

while True:
    try:
        l2 = info.l2_snapshot(COIN)
        mids = info.all_mids()
        state = info.user_state(addr)
        
        equity = float(state["marginSummary"]["accountValue"])
        free = equity - float(state["marginSummary"]["totalMarginUsed"])
        price = float(mids[COIN])
        
        pos, entry = 0.0, 0.0
        for p in state["assetPositions"]:
            if p["position"]["coin"] == COIN:
                pos = float(p["position"]["szi"]); entry = float(p["position"]["entryPx"])

        # ANALYSIS
        hist.append(price)
        if len(hist) > 100: hist.pop(0)
        z = (price - statistics.mean(hist)) / statistics.stdev(hist) if len(hist) > 20 else 0
        
        bids = sum(float(b['sz']) for b in l2['levels'][0][:5])
        asks = sum(float(a['sz']) for a in l2['levels'][1][:5])
        imb = bids / asks if asks > 0 else 1.0

        # --- SNIPER EXIT LOGIC ---
        if pos > 0:
            roi = (price - entry) / entry
            hwm = max(hwm, price)
            dd = (hwm - price) / hwm
            
            # Tiukennettu Sniper-kotiutus:
            # 1. Jos ROI > 0.5% ja hinta tippuu huipusta 0.15% (Nopea lukitus)
            # 2. Jos ROI > 0.8% (Heti ulos, ei ahneutta)
            # 3. Jos Imbalance kääntyy meitä vastaan nousussa
            if (roi > 0.005 and dd > 0.0015) or (roi > 0.008) or (roi > 0.003 and imb < 0.3):
                msg = f"🎯 SNIPER EXIT: ROI {roi*100:.2f}% | PnL: ${((price-entry)*pos):.2f}"
                print(f"\n{msg}"); log_event(msg)
                exch.market_close(COIN)
                time.sleep(10) # Rauhoitetaan konehuone
            elif roi < -0.035:
                print("\n🛡️ EMERGENCY SHIELD - STOP LOSS")
                exch.market_close(COIN); time.sleep(10)

        # --- SNIPER ENTRY (ONLY ON DEEP BLOOD) ---
        elif z < -2.3 and imb > 3.0:
            strike_usd = (equity * RISK_PCT) * LEVERAGE
            part_size = round((strike_usd/price) / 2, 1)
            print(f"🎭 SNIPER ENTRY 1/2 @ {price}")
            exch.market_open(COIN, True, part_size, price, 0.01)
            time.sleep(random.uniform(1, 3))
            exch.market_open(COIN, True, part_size, price, 0.01)
            last_trade_time = time.time(); hwm = price

        # HUD
        st = f"BATTLE ({LEVERAGE}x)" if pos > 0 else "SNIPER SCAN"
        pnl = (price-entry)*pos if pos > 0 else 0
        print(f"Z:{z:+.2f} | Imb:{imb:.1f} | Eq:${equity:.2f} | PnL:${pnl:+.2f} | {st}")
        time.sleep(1.0)

    except KeyboardInterrupt: break
    except Exception as e: print(f"⚠️ Telemetry Error: {e}"); time.sleep(5)
