""" Technical implementation for Hummingbot Gateway V2.1 - TITANIUM SHIELD """
import time, statistics, sys, getpass, json, os, datetime, random
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

# 1. SETUP
print("🦈 FERRARI V15.2 - TITANIUM SHIELD (FLASH CRASH PROTECT)")
print("-------------------------------------------------------")

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

# 2. CONFIGURATION
TARGET_COINS = ["HYPE", "PURR", "AI", "PEPE", "WIF", "SOL", "JUP", "TIA", "SUI"]
MAX_POSITIONS = 3
LEVERAGE = 7
RISK_PCT_PER_TRADE = 0.28
TRAILING_GAP = 0.008
TAKE_PROFIT_PCT = 0.025

# --- EMERGENCY BREAKER ---
START_EQUITY = 0 # Alustetaan lennosta
MAX_DRAWDOWN_PCT = 0.10 # Jos kassa sulaa -10% -> SULJE KAIKKI

peak_prices = {} 

def log_trade(msg):
    with open("megalodon_journal.txt", "a") as f:
        t = datetime.datetime.now().strftime('%H:%M:%S')
        f.write(f"[{t}] {msg}\n")

while True:
    try:
        # --- A. HALLINTAVAIHE (MANAGE) ---
        try:
            state = info.user_state(addr)
            mids = info.all_mids()
        except Exception as e:
            if "429" in str(e): time.sleep(10); continue
            else: time.sleep(1); continue

        equity = float(state["marginSummary"]["accountValue"])
        
        # Alustetaan aloitus-kassa (vain ensimmäisellä kierroksella)
        if START_EQUITY == 0: START_EQUITY = equity
        
        # 🚨 EMERGENCY CHECK: Jos kassa sulaa liikaa
        if equity < START_EQUITY * (1 - MAX_DRAWDOWN_PCT):
            print(f"\n☢️ EMERGENCY SHUTDOWN! Equity drop > 10%. Closing all.")
            for p in state["assetPositions"]:
                if float(p["position"]["szi"]) != 0:
                    exch.market_close(p["position"]["coin"])
            log_trade("SYSTEM EMERGENCY SHUTDOWN - DRAWDOWN LIMIT")
            sys.exit() # Pysäytä botti kokonaan

        raw_positions = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]
        active_coins = []
        status_items = []

        for p in raw_positions:
            pos = p["position"]
            coin = pos["coin"]
            active_coins.append(coin)
            if coin not in mids: continue

            sz = float(pos["szi"])
            entry = float(pos["entryPx"])
            curr_price = float(mids[coin])
            roi = (curr_price - entry) / entry if sz > 0 else (entry - curr_price) / entry
            
            if coin not in peak_prices: peak_prices[coin] = curr_price 
            if curr_price > peak_prices[coin]: peak_prices[coin] = curr_price
            
            dynamic_gap = TRAILING_GAP
            if roi > 0.015: dynamic_gap = 0.004
            
            stop_price = peak_prices[coin] * (1 - dynamic_gap)
            status_items.append(f"[{coin} {roi*100:+.1f}%]")

            if roi > TAKE_PROFIT_PCT or curr_price < stop_price:
                print(f"\n💰 EXIT {coin} (Profit/Stop hit)")
                exch.market_close(coin)
                log_trade(f"EXIT {coin} | ROI: {roi*100:.2f}%")
                if coin in peak_prices: del peak_prices[coin]
                time.sleep(2)
        
        # --- B. HYBRID SCANNING ---
        open_slots = MAX_POSITIONS - len(active_coins)
        status_str = f"Eq: ${equity:.1f} | {' '.join(status_items)}"
        
        if open_slots > 0:
            scan_batch = random.sample([c for c in TARGET_COINS if c not in active_coins], k=min(3, len(TARGET_COINS)))
            print(f"{status_str} | 📡 Shielded Scan...", end="\r")
            for coin in scan_batch:
                now_ms = int(time.time() * 1000)
                try:
                    c = info.candles_snapshot(coin, "5m", 20, now_ms)
                    time.sleep(0.3)
                except: continue
                if not c: continue
                closes = [float(x['c']) for x in c]; vols = [float(x['v']) for x in c]
                last_price = closes[-1]; prev_price = closes[-2]
                last_vol = vols[-1]; avg_vol = sum(vols[:-1]) / len(vols[:-1]) if vols[:-1] else 1
                
                # MOMENTUM & DIP
                if (last_vol/avg_vol > 2.5 and (last_price-prev_price)/prev_price > 0.002) or \
                   ((last_price-closes[-4])/closes[-4] < -0.025 and (last_price-prev_price)/prev_price > 0):
                    print(f"\n🚀 ENTRY {coin}")
                    size = round(((equity * RISK_PCT_PER_TRADE) * LEVERAGE) / last_price, 1)
                    if size > 0:
                        exch.market_open(coin, True, size, last_price, 0.01)
                        log_trade(f"ENTRY {coin}"); peak_prices[coin] = last_price
                        time.sleep(2); break
        else:
            print(f"{status_str} | 🔒 FULL HOUSE", end="\r")
        time.sleep(2) 
    except Exception as e:
        if "429" in str(e): time.sleep(10)
        else: print(f"\n⚠️ Error: {e}"); time.sleep(2)
