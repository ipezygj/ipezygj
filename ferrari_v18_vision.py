""" Technical implementation for Hummingbot Gateway V2.1 - APEX VISION V18 (PATTERN RECOGNITION) """
import time, statistics, sys, getpass, json, os, datetime, random
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

print("🦅 FERRARI V18 - VISION (ADAPTIVE REGIME + CANDLESTICK PATTERNS)")
print("---------------------------------------------------------------")

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
TARGET_COINS = ["SOL", "ETH", "BTC", "AVAX", "LINK", "ARB", "SUI", "TIA", "DOGE"]
MAX_POSITIONS = 3
LEVERAGE = 5
RISK_PCT = 0.25
START_EQUITY = 0 
MAX_DRAWDOWN_PCT = 0.10

# Strategy Params
BB_WINDOW = 20
BB_STD = 2.0
VOLATILITY_THRESHOLD = 0.004

def get_vision_signals(candles):
    """ Tunnistaa kynttiläkuviot: HAMMER, ENGULFING, NONE """
    if len(candles) < 3: return "NONE"
    
    c1, c2 = candles[-2], candles[-1] # Edellinen ja nykyinen kynttilä
    o1, h1, l1, cl1 = float(c1['o']), float(c1['h']), float(c1['l']), float(c1['c'])
    o2, h2, l2, cl2 = float(c2['o']), float(c2['h']), float(c2['l']), float(c2['c'])
    
    body2 = abs(cl2 - o2)
    lower_wick2 = min(o2, cl2) - l2
    upper_wick2 = h2 - max(o2, cl2)
    
    # 1. BULLISH HAMMER (Vahva osto-signaali pohjalta)
    if lower_wick2 > (body2 * 2) and upper_wick2 < (body2 * 0.5) and (h2-l2) > 0:
        return "BULLISH_HAMMER"
    
    # 2. BULLISH ENGULFING (Aggressiivinen osto)
    if cl2 > o2 and cl1 < o1 and cl2 > o1 and o2 < cl1:
        return "BULLISH_ENGULFING"
        
    # 3. BEARISH ENGULFING (Aggressiivinen myynti/short)
    if cl2 < o2 and cl1 > o1 and cl2 < o1 and o2 > cl1:
        return "BEARISH_ENGULFING"
        
    return "NONE"

def get_market_data(coin):
    now_ms = int(time.time() * 1000)
    try:
        c = info.candles_snapshot(coin, "1m", 30, now_ms)
        if not c or len(c) < 20: return None
    except: return None
    
    closes = [float(x['c']) for x in c]
    vols = [float(x['v']) for x in c]
    
    sma = statistics.mean(closes[-20:])
    std = statistics.stdev(closes[-20:])
    
    return {
        "price": closes[-1],
        "upper": sma + (std * BB_STD),
        "lower": sma - (std * BB_STD),
        "volat": std / sma,
        "vol_ratio": vols[-1] / (statistics.mean(vols[:-1]) or 1),
        "pattern": get_vision_signals(c)
    }

# --- 3. MAIN LOOP ---
while True:
    try:
        try:
            state = info.user_state(addr)
            mids = info.all_mids()
        except: time.sleep(2); continue

        equity = float(state["marginSummary"]["accountValue"])
        if START_EQUITY == 0: START_EQUITY = equity
        if equity < START_EQUITY * (1 - MAX_DRAWDOWN_PCT): sys.exit()

        raw_positions = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]
        active_coins = [p["position"]["coin"] for p in raw_positions]
        status_items = []

        # EXIT LOGIC
        for p in raw_positions:
            pos = p["position"]; coin = pos["coin"]; sz = float(pos["szi"])
            entry = float(pos["entryPx"]); curr = float(mids[coin])
            roi = (curr - entry) / entry if sz > 0 else (entry - curr) / entry
            
            side = "L" if sz > 0 else "S"
            status_items.append(f"[{side}:{coin} {roi*100:+.2f}%]")
            
            if roi > 0.015: exch.market_close(coin)
            elif roi < -0.012: exch.market_close(coin)
        
        # ENTRY LOGIC (VISION)
        if len(active_coins) < MAX_POSITIONS:
            scan_batch = random.sample([c for c in TARGET_COINS if c not in active_coins], k=min(4, len(TARGET_COINS)))
            print(f"Eq: ${equity:.1f} | {' '.join(status_items)} | 👁️ Vision Scanning...", end="\r")
            
            for coin in scan_batch:
                d = get_market_data(coin)
                if not d: continue
                
                is_buy, mode = None, ""
                
                # TILA A: HUNTER (Trend) - Volatiliteetti korkea
                if d["volat"] > VOLATILITY_THRESHOLD:
                    if d["price"] > d["upper"] and d["vol_ratio"] > 1.8:
                        if d["pattern"] == "BULLISH_ENGULFING": # Vahvistus
                            is_buy = True; mode = "HUNTER-LONG-V"
                    elif d["price"] < d["lower"] and d["vol_ratio"] > 1.8:
                        if d["pattern"] == "BEARISH_ENGULFING": # Vahvistus
                            is_buy = False; mode = "HUNTER-SHORT-V"

                # TILA B: FISHER (Range) - Volatiliteetti matala
                else:
                    if d["price"] < d["lower"]:
                        # Odotetaan Hammeria tai Engulfingia ennen kuin ostetaan dippi
                        if d["pattern"] in ["BULLISH_HAMMER", "BULLISH_ENGULFING"]:
                            is_buy = True; mode = "FISHER-LONG-V"
                    elif d["price"] > d["upper"]:
                        # Odotetaan Bearish Engulfingia ennen kuin shortataan huippu
                        if d["pattern"] == "BEARISH_ENGULFING":
                            is_buy = False; mode = "FISHER-SHORT-V"

                if is_buy is not None:
                    print(f"\n✨ VISION STRIKE [{mode}]: {coin} (Pattern: {d['pattern']})")
                    size = round(((equity * RISK_PCT) * LEVERAGE) / d["price"], 1)
                    if size > 0:
                        exch.market_open(coin, is_buy, size, d["price"], 0.01)
                        time.sleep(2); break
        else:
            print(f"Eq: ${equity:.1f} | {' '.join(status_items)} | 🔒 VISION FULL", end="\r")
        time.sleep(1)

    except Exception as e:
        time.sleep(2)
