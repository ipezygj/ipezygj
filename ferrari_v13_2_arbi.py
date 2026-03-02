""" Technical implementation for Hummingbot Gateway V2.1. """
import time, statistics, sys, getpass, json, os, datetime, random
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

# 1. SETUP
print("🕵️ FERRARI V13.2.1 - SCROLLING HUD ACTIVE")
print("-----------------------------------------")
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

def log_event(msg):
    with open("profits.txt", "a") as f:
        t = datetime.datetime.now().strftime("%H:%M:%S")
        f.write(f"[{t}] {msg}\n")

print(f"🏁 RADAR SYNCED | MAIN: {MAIN_COIN} | SECONDARY: {ARBI_COINS}")

while True:
    try:
        mids = info.all_mids()
        state = info.user_state(addr)
        equity = float(state["marginSummary"]["accountValue"])
        
        # Tarkistetaan positiot
        pos_data = None
        for p in state["assetPositions"]:
            if abs(float(p["position"]["szi"])) > 0:
                pos_data = p["position"]
                break
        
        # --- BATTLE HUD ---
        if pos_data:
            coin = pos_data["coin"]
            sz = float(pos_data["szi"])
            entry = float(pos_data["entryPx"])
            curr = float(mids[coin])
            roi = (curr - entry) / entry if sz > 0 else (entry - curr) / entry
            pnl = (curr - entry) * sz
            
            print(f"⚔️ [BATTLE] {coin} | ROI: {roi*100:+.2f}% | PnL: ${pnl:+.2f} | Eq: ${equity:.2f}")
            
            # Sniper Exit
            exit_trigger = 0.005 if coin == MAIN_COIN else 0.0035
            if roi > exit_trigger:
                print(f"🎯 SNIPER EXIT TRIGGERED!")
                exch.market_close(coin)
                log_event(f"WIN {coin}: {roi*100:.2f}%")
                time.sleep(10)
        
        # --- SCAN HUD ---
        else:
            for coin in [MAIN_COIN] + ARBI_COINS:
                px = float(mids[coin])
                
                # HYPE Z-Score laskenta
                z_display = "INIT"
                if coin == MAIN_COIN:
                    hist.append(px)
                    if len(hist) > 50: hist.pop(0)
                    if len(hist) > 10:
                        z = (px - statistics.mean(hist)) / statistics.stdev(hist)
                        z_display = f"{z:+.2f}"
                        if z < -2.4:
                            size = round(((equity * RISK_PCT) * LEVERAGE) / px, 1)
                            print(f"⚡ Z-DIP ATTACK: {coin} @ {px}")
                            exch.market_open(coin, True, size, px, 0.01)
                            log_event(f"ENTRY {coin} (Z-DIP)")
                
                # Arbi Scan (Esimerkki hintaeron haistelusta)
                # Tässä vaiheessa näytetään hinta ja status
                status = "STABLE" if coin != MAIN_COIN else f"Z:{z_display}"
                print(f"📡 SCAN | {coin:4} | Px: {px:8.4f} | {status} | Eq: ${equity:.2f}")
                time.sleep(0.4) # Rullaava efekti

    except Exception as e:
        print(f"⚠️ Telemetry Error: {e}")
        time.sleep(5)
