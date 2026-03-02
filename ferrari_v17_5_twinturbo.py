""" Technical implementation for Hummingbot Gateway V2.1 - APEX TWIN TURBO V17.5 (LONG/SHORT) """
import time, statistics, sys, getpass, json, os, datetime, random
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

print("🏎️ FERRARI V17.5 - TWIN TURBO (LONG & SHORT)")
print("---------------------------------------------")

# --- 1. SETUP ---
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

# --- 2. CONFIG ---
# Vain suuret kolikot Shorttaukseen (Vältä pieniä meemejä!)
TARGET_COINS = ["SOL", "ETH", "BTC", "AVAX", "LINK", "ARB", "SUI", "TIA", "DOGE"]
MAX_POSITIONS = 3
LEVERAGE = 5
RISK_PCT = 0.25
START_EQUITY = 0 
MAX_DRAWDOWN_PCT = 0.10

# Strategy Parameters
BB_WINDOW = 20
BB_STD = 2.0

def get_market_data(coin):
    now_ms = int(time.time() * 1000)
    try:
        c = info.candles_snapshot(coin, "1m", 25, now_ms)
        if not c or len(c) < 20: return None
    except: return None
    
    closes = [float(x['c']) for x in c]
    vols = [float(x['v']) for x in c]
    
    sma = statistics.mean(closes[-20:])
    std = statistics.stdev(closes[-20:])
    upper = sma + (std * BB_STD)
    lower = sma - (std * BB_STD)
    
    volatility = std / sma 
    avg_vol = statistics.mean(vols[:-1])
    vol_ratio = vols[-1] / avg_vol if avg_vol > 0 else 1
    
    return { "price": closes[-1], "upper": upper, "lower": lower, "volat": volatility, "vol_ratio": vol_ratio }

# --- 3. MAIN LOOP ---
while True:
    try:
        # A. POSITIOT (Päivitetty näyttämään Shortit oikein)
        try:
            state = info.user_state(addr)
            mids = info.all_mids()
        except: time.sleep(2); continue

        equity = float(state["marginSummary"]["accountValue"])
        if START_EQUITY == 0: START_EQUITY = equity
        
        if equity < START_EQUITY * (1 - MAX_DRAWDOWN_PCT): sys.exit()

        raw_positions = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]
        active_coins = []
        status_items = []

        for p in raw_positions:
            pos = p["position"]; coin = pos["coin"]; active_coins.append(coin)
            if coin not in mids: continue
            
            sz = float(pos["szi"]) # Positiivinen = Long, Negatiivinen = Short
            entry = float(pos["entryPx"]); curr = float(mids[coin])
            
            # ROI Laskenta (Toimii nyt myös Shorteille)
            if sz > 0: roi = (curr - entry) / entry      # Long
            else:      roi = (entry - curr) / entry      # Short
            
            # Smart Exit (Short/Long agnostic)
            target = 0.015 
            stop = -0.01   
            
            side_str = "L" if sz > 0 else "S"
            status_items.append(f"[{side_str}:{coin} {roi*100:+.2f}%]")
            
            if roi > target: 
                print(f"\n💰 TAKE PROFIT ({side_str}): {coin}"); exch.market_close(coin)
            elif roi < stop:
                print(f"\n🛡️ STOP LOSS ({side_str}): {coin}"); exch.market_close(coin)
        
        # B. TWIN TURBO SCANNING
        open_slots = MAX_POSITIONS - len(active_coins)
        status_str = f"Eq: ${equity:.1f} | {' '.join(status_items)}"
        
        if open_slots > 0:
            scan_batch = random.sample([c for c in TARGET_COINS if c not in active_coins], k=min(5, len(TARGET_COINS)))
            print(f"{status_str} | 🦅 Scanning Long/Short...", end="\r")
            
            for coin in scan_batch:
                d = get_market_data(coin)
                if not d: continue
                price = d["price"]; volat = d["volat"]; upper = d["upper"]; lower = d["lower"]
                
                # --- LOGIIKKA ---
                is_buy = None
                mode = ""
                
                # 1. HUNTER MODE (Trend) - Volatiliteetti korkea
                if volat > 0.004:
                    if price > upper and d["vol_ratio"] > 2.0:
                        is_buy = True; mode = "HUNTER-LONG"
                    elif price < lower and d["vol_ratio"] > 2.0:
                        is_buy = False; mode = "HUNTER-SHORT" # Paniikki-myynti
                
                # 2. FISHER MODE (Range) - Volatiliteetti matala
                else:
                    if price < lower:
                        is_buy = True; mode = "FISHER-LONG"   # Osta dippi
                    elif price > upper:
                        is_buy = False; mode = "FISHER-SHORT" # Shorttaa huippu
                
                # EXECUTE
                if is_buy is not None:
                    print(f"\n⚡ {mode}: {coin} (Price:{price})")
                    size = round(((equity * RISK_PCT) * LEVERAGE) / price, 1)
                    if size > 0:
                        exch.market_open(coin, is_buy, size, price, 0.01)
                        time.sleep(2); break

        else:
            print(f"{status_str} | 🔒 FULL HOUSE", end="\r")
        time.sleep(1)

    except Exception as e:
        time.sleep(2)
