""" Technical implementation for Hummingbot Gateway V2.1 - GANDALF V15.5 (OI + FUNDING) """
import time, statistics, sys, getpass, json, os, datetime, random
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

print("🧙‍♂️ FERRARI V15.5 - GANDALF'S STAFF (DEEP MARKET WISDOM)")
print("-------------------------------------------------------")

# --- 1. SETUP & AUTHENTICATION ---
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

# --- 2. CONFIGURATION ---
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

# --- 3. GANDALF'S DEEP SIGHT (HELPER) ---
def get_deep_wisdom(coin_name):
    """ Fetches Open Interest and Funding to confirm validity. """
    try:
        # Hakee koko markkinan tilan (raskas kutsu, käytetään vain signaalissa)
        meta_state = info.meta_and_asset_ctxs()
        universe = meta_state[0]["universe"]
        asset_ctxs = meta_state[1]
        
        # Etsi kolikon indeksi universumista
        coin_idx = -1
        for idx, u in enumerate(universe):
            if u["name"] == coin_name:
                coin_idx = idx
                break
        
        if coin_idx == -1: return None
        
        # Analysoi konteksti
        ctx = asset_ctxs[coin_idx]
        funding = float(ctx["funding"])
        open_interest = float(ctx["openInterest"])
        
        return {"oi": open_interest, "funding": funding}
    except Exception as e:
        return None

def log_trade(msg):
    with open("megalodon_journal.txt", "a") as f:
        t = datetime.datetime.now().strftime('%H:%M:%S')
        f.write(f"[{t}] {msg}\n")

# --- 4. MAIN LOOP ---
while True:
    try:
        # A. SALKKU JA PANSSARI
        try:
            state = info.user_state(addr)
            mids = info.all_mids()
        except Exception as e:
            if "429" in str(e): time.sleep(10); continue
            else: time.sleep(1); continue

        equity = float(state["marginSummary"]["accountValue"])
        if START_EQUITY == 0: START_EQUITY = equity
        
        # Emergency Shield (Titanium)
        if equity < START_EQUITY * (1 - MAX_DRAWDOWN_PCT):
            print("🧙‍♂️ 'You shall not pass!' (Max Drawdown Limit Hit)")
            for p in state["assetPositions"]:
                if float(p["position"]["szi"]) != 0: exch.market_close(p["position"]["coin"])
            sys.exit()

        raw_positions = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]
        active_coins = []
        status_items = []

        # Position Management (The Shepard)
        for p in raw_positions:
            pos = p["position"]; coin = pos["coin"]; active_coins.append(coin)
            if coin not in mids: continue
            
            sz = float(pos["szi"]); entry = float(pos["entryPx"]); curr_price = float(mids[coin])
            roi = (curr_price - entry) / entry if sz > 0 else (entry - curr_price) / entry
            
            if coin not in peak_prices: peak_prices[coin] = curr_price 
            if curr_price > peak_prices[coin]: peak_prices[coin] = curr_price
            
            # Snake Bite Logic
            dynamic_gap = TRAILING_GAP
            if roi > 0.015: dynamic_gap = 0.004 # Kiristä otetta
            
            stop_price = peak_prices[coin] * (1 - dynamic_gap)
            status_items.append(f"[{coin} {roi*100:+.1f}%]")

            if roi > TAKE_PROFIT_PCT or curr_price < stop_price:
                print(f"\n✨ GANDALF EXIT: {coin} | ROI: {roi*100:.2f}%")
                exch.market_close(coin)
                if coin in peak_prices: del peak_prices[coin]
        
        # B. THE WIZARD'S SCAN
        open_slots = MAX_POSITIONS - len(active_coins)
        status_str = f"Eq: ${equity:.1f} | {' '.join(status_items)}"
        
        if open_slots > 0:
            scan_batch = random.sample([c for c in TARGET_COINS if c not in active_coins], k=min(5, len(TARGET_COINS)))
            print(f"{status_str} | 👁️ Deep Scan...", end="\r")
            
            for coin in scan_batch:
                now_ms = int(time.time() * 1000)
                try:
                    c = info.candles_snapshot(coin, "1m", 15, now_ms)
                    time.sleep(0.2)
                except: continue
                if not c: continue
                
                closes = [float(x['c']) for x in c]; vols = [float(x['v']) for x in c]
                last_price = closes[-1]; prev_price = closes[-2]; last_vol = vols[-1]
                avg_vol = sum(vols[:-1]) / len(vols[:-1]) if vols[:-1] else 1
                
                # 1. TECHNICAL TRIGGER (Nopea sihti)
                vol_ratio = last_vol / avg_vol
                price_change = (last_price - prev_price) / prev_price
                
                if vol_ratio > 2.2 and price_change > 0.0025: # Hieman löysempi volyymi, koska OI tarkistaa
                    # 2. GANDALF'S CONFIRMATION (Syvä viisaus)
                    print(f"\n🔮 Consulting the Oracles for {coin}...")
                    wisdom = get_deep_wisdom(coin)
                    
                    if wisdom:
                        # Onko rahoitus neutraali/negatiivinen? (Vältä ruuhkaa)
                        funding_ok = wisdom["funding"] < 0.0004 
                        # Onko OI "elossa"? (Emme halua kuollutta rahaa)
                        oi_ok = wisdom["oi"] > 50000 
                        
                        if funding_ok and oi_ok:
                            print(f"⚡ GANDALF STRIKE: {coin} (Vol:{vol_ratio:.1f}x | OI:Active)")
                            size = round(((equity * RISK_PCT_PER_TRADE) * LEVERAGE) / last_price, 1)
                            if size > 0:
                                exch.market_open(coin, True, size, last_price, 0.01)
                                log_trade(f"GANDALF ENTRY {coin} | OI Checked")
                                peak_prices[coin] = last_price
                                time.sleep(2); break
                        else:
                            print(f"✋ Denied by Wisdom (High Funding or Low OI)")
                    time.sleep(1)

        else:
            print(f"{status_str} | 🛡️ FELLOWSHIP FULL", end="\r")
        time.sleep(1)
    except Exception as e:
        time.sleep(2)
