""" Technical implementation for Hummingbot Gateway V2.1 - PREDATOR V15.3 """
import time, statistics, sys, getpass, json, os, datetime, random
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

print("🦈 FERRARI V15.3 - PREDATOR (WIDE SCAN + FAST EXECUTION)")
print("-------------------------------------------------------")

# SETUP (Samat kuin ennen)
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

# --- 2. CONFIGURATION (LAAJENNETTU LISTA) ---
# Lisätty volyymia ja likviditeettiä omaavia pareja
TARGET_COINS = [
    "HYPE", "PURR", "AI", "PEPE", "WIF", "SOL", "JUP", "TIA", "SUI", 
    "BTC", "ETH", "AVAX", "OP", "ARB", "LINK", "PENDLE", "ONDO", 
    "POPCAT", "GOAT", "ZEREBRO", "FARTCOIN", "TRUMP", "MELANIA"
]
MAX_POSITIONS = 3
LEVERAGE = 7
RISK_PCT_PER_TRADE = 0.28
TRAILING_GAP = 0.008
TAKE_PROFIT_PCT = 0.025
START_EQUITY = 0 
MAX_DRAWDOWN_PCT = 0.10
peak_prices = {} 

while True:
    try:
        try:
            state = info.user_state(addr)
            mids = info.all_mids()
        except Exception as e:
            if "429" in str(e): time.sleep(10); continue
            else: time.sleep(1); continue

        equity = float(state["marginSummary"]["accountValue"])
        if START_EQUITY == 0: START_EQUITY = equity
        
        # EMERGENCY SHIELD
        if equity < START_EQUITY * (1 - MAX_DRAWDOWN_PCT):
            for p in state["assetPositions"]:
                if float(p["position"]["szi"]) != 0: exch.market_close(p["position"]["coin"])
            sys.exit()

        raw_positions = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]
        active_coins = []
        status_items = []

        for p in raw_positions:
            pos = p["position"]; coin = pos["coin"]; active_coins.append(coin)
            if coin not in mids: continue
            sz = float(pos["szi"]); entry = float(pos["entryPx"]); curr_price = float(mids[coin])
            roi = (curr_price - entry) / entry if sz > 0 else (entry - curr_price) / entry
            if coin not in peak_prices: peak_prices[coin] = curr_price 
            if curr_price > peak_prices[coin]: peak_prices[coin] = curr_price
            dynamic_gap = TRAILING_GAP
            if roi > 0.015: dynamic_gap = 0.004
            stop_price = peak_prices[coin] * (1 - dynamic_gap)
            status_items.append(f"[{coin} {roi*100:+.1f}%]")
            if roi > TAKE_PROFIT_PCT or curr_price < stop_price:
                exch.market_close(coin)
                if coin in peak_prices: del peak_prices[coin]
        
        # --- B. WIDE PREDATOR SCAN (1min kynttilät nopeaan reaktioon) ---
        open_slots = MAX_POSITIONS - len(active_coins)
        status_str = f"Eq: ${equity:.1f} | {' '.join(status_items)}"
        
        if open_slots > 0:
            # Skannataan 5 satunnaista kolikkoa laajalta listalta per kierros
            scan_batch = random.sample([c for c in TARGET_COINS if c not in active_coins], k=min(5, len(TARGET_COINS)))
            print(f"{status_str} | 📡 Predator Scan ({len(TARGET_COINS)} assets)...", end="\r")
            
            for coin in scan_batch:
                now_ms = int(time.time() * 1000)
                try:
                    c = info.candles_snapshot(coin, "1m", 20, now_ms) # 1min = Nopeus
                    time.sleep(0.2)
                except: continue
                if not c: continue
                closes = [float(x['c']) for x in c]; vols = [float(x['v']) for x in c]
                last_price = closes[-1]; prev_price = closes[-2]; last_vol = vols[-1]
                avg_vol = sum(vols[:-1]) / len(vols[:-1]) if vols[:-1] else 1
                
                # MOMENTUM (Tiukka 2.5x raja säilyy)
                if last_vol / avg_vol > 2.5 and (last_price - prev_price) / prev_price > 0.002:
                    print(f"\n🚀 PREDATOR ENTRY: {coin}")
                    size = round(((equity * RISK_PCT_PER_TRADE) * LEVERAGE) / last_price, 1)
                    if size > 0:
                        exch.market_open(coin, True, size, last_price, 0.01)
                        peak_prices[coin] = last_price
                        time.sleep(2); break
        else:
            print(f"{status_str} | 🔒 FULL HOUSE", end="\r")
        time.sleep(1) # Nopeampi sykli
    except Exception as e:
        time.sleep(2)
