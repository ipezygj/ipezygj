""" Technical implementation for Hummingbot Gateway V2.1. """
import time, statistics, sys, getpass, json, os, datetime, random
from collections import deque
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

# 1. SETUP
print("🕵️ FERRARI V13.3 - DEEP WHALE-PROOF")
print("-----------------------------------")
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

# 2. CONFIGURATION
MAIN_COIN = "HYPE"
ARBI_COINS = ["ARB", "ETH", "SOL"]
LEVERAGE = 4
RISK_PCT = 0.35
hist = []
# PERSISTENCY LOCK: Tallennetaan viimeiset 5 imbalance-lukemaa (n. 3-4 sekuntia)
imb_buffer = deque(maxlen=5)

def log_event(msg):
    with open("profits.txt", "a") as f:
        t = datetime.datetime.now().strftime("%H:%M:%S")
        f.write(f"[{t}] {msg}\n")

print(f"🏁 WHALE-PROOF ACTIVE | LOCK-TIME: 3s | MIN_IMB: 5.0")

while True:
    try:
        mids = info.all_mids()
        state = info.user_state(addr)
        equity = float(state["marginSummary"]["accountValue"])
        
        pos_data = None
        for p in state["assetPositions"]:
            if abs(float(p["position"]["szi"])) > 0:
                pos_data = p["position"]
                break
        
        # --- BATTLE MODE ---
        if pos_data:
            coin = pos_data["coin"]
            sz = float(pos_data["szi"]); entry = float(pos_data["entryPx"])
            curr = float(mids[coin])
            roi = (curr - entry) / entry if sz > 0 else (entry - curr) / entry
            print(f"⚔️ BATTLE: {coin} | ROI: {roi*100:+.2f}% | Eq: ${equity:.2f}")
            
            if roi > 0.006 or (roi > 0.003 and random.random() < 0.1): # Sniper Exit
                print(f"🎯 SNIPER EXIT!")
                exch.market_close(coin)
                log_event(f"WIN {coin} ROI {roi*100:.2f}%")
                time.sleep(10)

        # --- SCAN MODE ---
        else:
            l2 = info.l2_snapshot(MAIN_COIN)
            bids = sum(float(b['sz']) for b in l2['levels'][0][:3])
            asks = sum(float(a['sz']) for a in l2['levels'][1][:3])
            curr_imb = bids / asks if asks > 0 else 1.0
            imb_buffer.append(curr_imb)
            
            px = float(mids[MAIN_COIN])
            hist.append(px)
            if len(hist) > 60: hist.pop(0)
            
            z = (px - statistics.mean(hist)) / statistics.stdev(hist) if len(hist) > 20 else 0
            
            # WHALE-PROOF CHECK: Onko imbalance ollut vakaa ja korkea?
            avg_imb = sum(imb_buffer) / len(imb_buffer)
            is_stable = all(i > 2.5 for i in imb_buffer) # Kaikki puskurissa yli 2.5
            
            print(f"📡 SCAN | Z:{z:+.2f} | Imb:{curr_imb:.1f} (Avg:{avg_imb:.1f}) | Buff:{len(imb_buffer)}/5")
            
            if z < -2.6 and avg_imb > 5.0 and is_stable:
                print(f"🐋 WHALE DETECTED & VERIFIED! ATTACKING...")
                size = round(((equity * RISK_PCT) * LEVERAGE) / px, 1)
                exch.market_open(MAIN_COIN, True, size, px, 0.01)
                log_event(f"ENTRY {MAIN_COIN} (WHALE-PROOF)")
                time.sleep(5)
            
            time.sleep(0.7) # Sykli n. 0.7-1.0s

    except Exception as e:
        print(f"⚠️ Error: {e}"); time.sleep(5)
