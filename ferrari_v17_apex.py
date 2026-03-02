""" Technical implementation for Hummingbot Gateway V2.1 - APEX V17 (HYBRID ADAPTIVE) """
import time, statistics, sys, getpass, json, os, datetime, random, math
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

print("🦁 FERRARI V17 - APEX PREDATOR (ADAPTIVE REGIME SWITCHING)")
print("----------------------------------------------------------")

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
TARGET_COINS = [
    "SOL", "ETH", "BTC", "AVAX", "LINK", "ARB", "SUI", "TIA", 
    "PEPE", "WIF", "DOGE", "CRV", "LDO"
]
MAX_POSITIONS = 3
LEVERAGE = 6
RISK_PCT = 0.25
START_EQUITY = 0 
MAX_DRAWDOWN_PCT = 0.10

# Strategy Parameters
BB_WINDOW = 20
BB_STD = 2.0
VOLATILITY_THRESHOLD = 0.008  # 0.8% liike minuutissa erottaa Trendin Rangesta

def get_market_data(coin):
    """ Hakee kynttilät ja laskee indikaattorit """
    now_ms = int(time.time() * 1000)
    try:
        c = info.candles_snapshot(coin, "1m", 25, now_ms)
        if not c or len(c) < 20: return None
    except: return None
    
    closes = [float(x['c']) for x in c]
    vols = [float(x['v']) for x in c]
    
    # Bollinger Bands
    sma = statistics.mean(closes[-20:])
    std = statistics.stdev(closes[-20:])
    upper = sma + (std * BB_STD)
    lower = sma - (std * BB_STD)
    
    # Volatiliteetti (Suhteellinen standard deviation)
    volatility = std / sma 
    
    # Volume Delta
    avg_vol = statistics.mean(vols[:-1])
    curr_vol = vols[-1]
    vol_ratio = curr_vol / avg_vol if avg_vol > 0 else 1
    
    return {
        "price": closes[-1],
        "upper": upper,
        "lower": lower,
        "sma": sma,
        "volatility": volatility,
        "vol_ratio": vol_ratio
    }

# --- 3. MAIN LOOP ---
while True:
    try:
        # A. POSITIOT & SUOJAUS
        try:
            state = info.user_state(addr)
            mids = info.all_mids()
        except: time.sleep(2); continue

        equity = float(state["marginSummary"]["accountValue"])
        if START_EQUITY == 0: START_EQUITY = equity
        
        # Titanium Shield
        if equity < START_EQUITY * (1 - MAX_DRAWDOWN_PCT):
            sys.exit()

        raw_positions = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]
        active_coins = []
        status_items = []

        for p in raw_positions:
            pos = p["position"]; coin = pos["coin"]; active_coins.append(coin)
            if coin not in mids: continue
            sz = float(pos["szi"]); entry = float(pos["entryPx"]); curr = float(mids[coin])
            roi = (curr - entry) / entry if sz > 0 else (entry - curr) / entry
            
            # Smart Exit (Riippuu strategiasta, mutta pidetään yksinkertaisena)
            target = 0.015 # 1.5% tavoite
            stop = -0.01   # 1% stop
            
            status_items.append(f"[{coin} {roi*100:+.2f}%]")
            if roi > target: 
                print(f"\n💰 TAKE PROFIT: {coin}"); exch.market_close(coin)
            elif roi < stop:
                print(f"\n🛡️ STOP LOSS: {coin}"); exch.market_close(coin)
        
        # B. APEX SCANNING (THE HYBRID BRAIN)
        open_slots = MAX_POSITIONS - len(active_coins)
        status_str = f"Eq: ${equity:.1f} | {' '.join(status_items)}"
        
        if open_slots > 0:
            scan_batch = random.sample([c for c in TARGET_COINS if c not in active_coins], k=min(5, len(TARGET_COINS)))
            print(f"{status_str} | 🧠 Analysing Regimes...", end="\r")
            
            for coin in scan_batch:
                data = get_market_data(coin)
                if not data: continue
                
                price = data["price"]
                volat = data["volatility"]
                
                # --- STRATEGY SWITCHING LOGIC ---
                
                # TILA 1: HIGH VOLATILITY -> HUNTER MODE (Momentum)
                # Jos markkina liikkuu kovaa (volat > 0.4%), etsimme läpimurtoa (Breakout)
                if volat > 0.004:
                    # Ehto: Hinta rikkoo YLÄNAUHAN ja Volyymi on kova
                    if price > data["upper"] and data["vol_ratio"] > 2.0:
                        print(f"\n🚀 HUNTER MODE (Trend): {coin} (Volat:{volat*100:.2f}% | Vol:{data['vol_ratio']:.1f}x)")
                        size = round(((equity * RISK_PCT) * LEVERAGE) / price, 1)
                        if size > 0:
                            exch.market_open(coin, True, size, price, 0.01)
                            time.sleep(2); break

                # TILA 2: LOW VOLATILITY -> FISHER MODE (Mean Reversion)
                # Jos markkina on rauhallinen (volat < 0.4%), ostamme dippejä
                else:
                    # Ehto: Hinta koskettaa ALANAUHAA (Oversold)
                    if price < data["lower"]:
                        dist = (data["lower"] - price) / price
                        print(f"\n🎣 FISHER MODE (Scalp): {coin} (Dip:{dist*100:.2f}% | Calm Market)")
                        size = round(((equity * RISK_PCT) * LEVERAGE) / price, 1)
                        if size > 0:
                            exch.market_open(coin, True, size, price, 0.01)
                            time.sleep(2); break

        else:
            print(f"{status_str} | 🔒 FULL HOUSE", end="\r")
        time.sleep(1)

    except Exception as e:
        time.sleep(2)
