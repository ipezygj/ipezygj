""" Technical implementation for Hummingbot Gateway V2.1 - STEALTH PACER """
import time, statistics, sys, getpass, json, os, datetime, random
from collections import deque
from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

# 1. SETUP
print("🦈 FERRARI V14.1.3 - STEALTH PACER (ANTI-BAN)")
print("---------------------------------------------")

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
MAX_POSITIONS = 2
LEVERAGE = 7
RISK_PCT_PER_TRADE = 0.35
VOL_TRIGGER = 2.5
TRAILING_GAP = 0.008

# Muisti trailing stopeille
peak_prices = {} 

def log_trade(msg):
    with open("megalodon_journal.txt", "a") as f:
        t = datetime.datetime.now().strftime('%H:%M:%S')
        f.write(f"[{t}] {msg}\n")

print(f"🌊 HUNTING GROUNDS: {len(TARGET_COINS)} Assets | MAX POS: {MAX_POSITIONS}")

while True:
    try:
        # --- A. HALLINTAVAIHE (MANAGE) ---
        try:
            state = info.user_state(addr)
            mids = info.all_mids()
        except Exception as e:
            if "429" in str(e):
                print("\n⚠️ API LIMIT HIT (429). Cooling down 10s...", end="\r")
                time.sleep(10)
                continue
            else:
                time.sleep(1)
                continue

        equity = float(state["marginSummary"]["accountValue"])
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
            
            # Trailing Logic
            if coin not in peak_prices: peak_prices[coin] = curr_price 
            if curr_price > peak_prices[coin]: peak_prices[coin] = curr_price
            
            stop_price = peak_prices[coin] * (1 - TRAILING_GAP)
            status_items.append(f"[{coin} {roi*100:+.1f}% STP:{stop_price:.4f}]")

            # EXIT CHECK
            if curr_price < stop_price:
                print(f"\n💰 BANKING PROFIT! {coin} hit Trailing Stop.")
                exch.market_close(coin)
                log_trade(f"EXIT {coin} | ROI: {roi*100:.2f}% | PnL Secured")
                if coin in peak_prices: del peak_prices[coin]
                time.sleep(2)
        
        # --- B. METSÄSTYSVAIHE (SMART SCAN) ---
        open_slots = MAX_POSITIONS - len(active_coins)
        status_str = f"Eq: ${equity:.0f} | {' '.join(status_items)}"
        
        if open_slots > 0:
            # SÄÄSTÖLIEKKI: Valitaan vain 3 satunnaista kohdetta skannattavaksi per kierros
            scan_batch = random.sample([c for c in TARGET_COINS if c not in active_coins], k=min(3, len(TARGET_COINS)))
            
            print(f"{status_str} | 📡 Scan: {len(scan_batch)} random...", end="\r")
            
            for coin in scan_batch:
                now_ms = int(time.time() * 1000)
                try:
                    c = info.candles_snapshot(coin, "1m", 25, now_ms)
                    time.sleep(0.3) # Pieni hengähdys kutsujen välillä
                except: continue

                if not c: continue
                
                last_vol = float(c[-1]['v'])
                last_close = float(c[-1]['c'])
                avg_vol = sum(float(x['v']) for x in c[-21:-1]) / 20
                if avg_vol == 0: continue
                
                vol_ratio = last_vol / avg_vol
                
                if vol_ratio > VOL_TRIGGER:
                    prev_close = float(c[-2]['c'])
                    change = (last_close - prev_close) / prev_close
                    
                    if change > 0.002:
                        print(f"\n🚀 DOUBLE IMPACT! {coin} Vol: {vol_ratio:.1f}x")
                        size = round(((equity * RISK_PCT_PER_TRADE) * LEVERAGE) / last_close, 1)
                        if size > 0:
                            exch.market_open(coin, True, size, last_close, 0.01)
                            log_trade(f"ENTRY {coin} | Vol: {vol_ratio:.1f}x")
                            peak_prices[coin] = last_close
                            time.sleep(2)
                            break
        else:
            print(f"{status_str} | 🔒 Full Capacity", end="\r")

        time.sleep(2) 

    except Exception as e:
        if "429" in str(e):
             print("\n⚠️ API LIMIT HIT (429). Cooling down 10s...", end="\r")
             time.sleep(10)
        else:
            print(f"\n⚠️ Ignored Error: {e}"); time.sleep(2)
