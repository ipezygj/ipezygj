""" Technical implementation for Hummingbot Gateway V2.1 - EXIT NEUVOSTO V19.9 """
import time, statistics, sys, getpass, json, os, random, csv
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

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
MAX_POSITIONS = 3; LEVERAGE = 5; START_EQUITY = 0 
BASE_RISK_PCT = 0.25 
SHADOW_LOG = "shadow_data.csv"
brain_thoughts = ["System initialize..."]
last_scan_result = "Waiting for data..."

def add_thought(text):
    global brain_thoughts
    timestamp = time.strftime("%H:%M:%S")
    brain_thoughts.insert(0, f"[{timestamp}] {text}")
    brain_thoughts = brain_thoughts[:6]

def record_shadow_event(coin, signal, price, status):
    file_exists = os.path.isfile(SHADOW_LOG)
    with open(SHADOW_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists: writer.writerow(['timestamp', 'coin', 'signal', 'price', 'status'])
        writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), coin, signal, price, status])

# --- 3. HELPER FUNCTIONS ---
def get_vision_signals(candles):
    if len(candles) < 3: return "NONE"
    c1, c2 = candles[-2], candles[-1]
    o1, h1, l1, cl1 = float(c1['o']), float(c1['h']), float(c1['l']), float(c1['c'])
    o2, h2, l2, cl2 = float(c2['o']), float(c2['h']), float(c2['l']), float(c2['c'])
    if cl2 > o2 and (o2 - l2) > (abs(cl2-o2)*1.5): return "BULLISH_HAMMER"
    if cl2 > o2 and cl1 < o1 and cl2 > o1: return "BULLISH_ENGULFING"
    if cl2 < o2 and cl1 > o1 and cl2 < o1: return "BEARISH_ENGULFING"
    return "NONE"

def get_market_data(coin):
    try:
        c = info.candles_snapshot(coin, "1m", 25, int(time.time() * 1000))
        closes = [float(x['c']) for x in c]
        sma = statistics.mean(closes[-20:]); std = statistics.stdev(closes[-20:])
        volatility_pct = (std / closes[-1]) * 100 
        return {
            "price": closes[-1], "lower": sma - (std * 2.0), "upper": sma + (std * 2.0),
            "std": std, "volatility": volatility_pct,
            "pattern": get_vision_signals(c)
        }
    except: return None

# --- 4. BRAINS ---
def brain_alpha_technician(d):
    if d["pattern"] in ["BULLISH_HAMMER", "BULLISH_ENGULFING"]: return "LONG"
    if d["pattern"] == "BEARISH_ENGULFING": return "SHORT"
    if d["price"] < d["lower"]: return "LONG"
    if d["price"] > d["upper"]: return "SHORT"
    return "NEUTRAL"

def brain_beta_oracle(coin):
    try:
        c = info.candles_snapshot(coin, "5m", 10, int(time.time() * 1000))
        closes = [float(x['c']) for x in c]
        if statistics.mean(closes[-3:]) > statistics.mean(closes[-10:]): return "LONG_OK"
        if statistics.mean(closes[-3:]) < statistics.mean(closes[-10:]): return "SHORT_OK"
    except: pass
    return "WAIT"

def brain_gamma_sentinel(coin):
    try:
        l2 = info.l2_snapshot(coin)
        bids = sum([float(x['sz']) for x in l2['levels'][0][:3]])
        asks = sum([float(x['sz']) for x in l2['levels'][1][:3]])
        ratio = bids / asks if asks > 0 else 1.0
        if ratio > 2.0: return "BULLS_DOMINATING"
        if ratio < 0.5: return "BEARS_DOMINATING"
    except: pass
    return "STABLE"

# --- 5. MAIN ENGINE ---
while True:
    try:
        state = info.user_state(addr); mids = info.all_mids()
        equity = float(state["marginSummary"]["accountValue"])
        if START_EQUITY == 0: START_EQUITY = equity
        raw_pos = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]
        
        os.system('clear')
        print(f"🏎️  FERRARI TELEMETRY | Eq: ${equity:.2f} | Net: {((equity-START_EQUITY)/START_EQUITY)*100:+.2f}%")
        print(f"📡 SCANNER: {last_scan_result}")
        print("-" * 65)
        
        print(f"{'COIN':<8} {'SIDE':<6} {'SIZE':<10} {'ENTRY':<10} {'ROI%':<8}")
        active_coins = []
        for p in raw_pos:
            pos = p["position"]; coin = pos["coin"]; sz = float(pos["szi"])
            entry = float(pos["entryPx"]); curr = float(mids[coin])
            roi = (curr - entry) / entry if sz > 0 else (entry - curr) / entry
            active_coins.append(coin)
            print(f"{coin:<8} {'LONG' if sz > 0 else 'SHORT':<6} {abs(sz):<10.2f} {entry:<10.2f} {roi*100:>+7.2f}%")
            
            # --- UUSI NEUVOSTO-POHJAINEN EXIT ---
            sig_c = brain_gamma_sentinel(coin)
            
            # 1. STOP LOSS (Ehdoton suoja)
            if roi < -0.012:
                add_thought(f"🛡️ EMERGENCY STOP on {coin}!"); exch.market_close(coin)
            
            # 2. NEUVOSTO-TAKE PROFIT (Dynaaminen)
            # Jos ollaan voitolla > 0.8%
            elif roi > 0.008:
                # Jos ollaan LONG ja myyjät alkavat voittaa TAI ROI on jo todella iso
                if sz > 0 and (sig_c == "BEARS_DOMINATING" or roi > 0.025):
                    add_thought(f"💰 COUNCIL TP on {coin} (ROI:{roi*100:.2f}%)")
                    exch.market_close(coin)
                # Jos ollaan SHORT ja ostajat alkavat voittaa
                elif sz < 0 and (sig_c == "BULLS_DOMINATING" or roi > 0.025):
                    add_thought(f"💰 COUNCIL TP on {coin} (ROI:{roi*100:.2f}%)")
                    exch.market_close(coin)
                else:
                    # Neuvosto antaa jatkaa (Hold the line)
                    if random.random() < 0.1: # Vähennetään loki-spämmiä
                        add_thought(f"💎 COUNCIL: Hold {coin}... Let it run.")

        print("-" * 65)
        print("🧠 TRIAD COUNCIL (Log):")
        for thought in brain_thoughts: print(f"  {thought}")
        print("-" * 65)

        # ENTRY SCANNING... (Sama kuin ennen)
        if len(active_coins) < MAX_POSITIONS:
            coin = random.choice([c for c in TARGET_COINS if c not in active_coins])
            d = get_market_data(coin)
            if d:
                status_icon = "🟢" if d['volatility'] < 0.30 else "🔴"
                last_scan_result = f"Checking {coin}... Vola:{d['volatility']:.2f}% {status_icon} | Pat:{d['pattern']}"
                sig_a = brain_alpha_technician(d)
                if sig_a != "NEUTRAL":
                    sig_b = brain_beta_oracle(coin)
                    sig_c = brain_gamma_sentinel(coin)
                    # Heisenberg risk scaler
                    risk_scaler = 1.0
                    if d["volatility"] > 0.15: risk_scaler = 0.7
                    if d["volatility"] > 0.30: risk_scaler = 0.4
                    size = ((equity * (BASE_RISK_PCT * risk_scaler)) * LEVERAGE) / d["price"]
                    
                    if sig_a == "LONG" and sig_b == "LONG_OK" and sig_c != "BEARS_DOMINATING":
                        add_thought(f"✅ UNANIMOUS: Long {coin}")
                        exch.market_open(coin, True, round(size, 1), d["price"], 0.01)
                        time.sleep(2)
                    elif sig_a == "SHORT" and sig_b == "SHORT_OK" and sig_c != "BULLS_DOMINATING":
                        add_thought(f"✅ UNANIMOUS: Short {coin}")
                        exch.market_open(coin, False, round(size, 1), d["price"], 0.01)
                        time.sleep(2)
                    else:
                        add_thought(f"❌ VETO[B:{sig_b},C:{sig_c}] for {coin}")

        time.sleep(2)
    except Exception as e:
        last_scan_result = f"⚠️ Error: {str(e)}"
        time.sleep(5)
