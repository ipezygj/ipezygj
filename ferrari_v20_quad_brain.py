""" Technical implementation for Hummingbot Gateway V2.1 - BLACK BOX V26.0 """
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

TARGET_COINS = ["SOL", "ETH", "AVAX", "LINK", "ARB", "SUI", "TIA", "DOGE"]
MAX_POSITIONS = 3; LEVERAGE = 5; START_EQUITY = 0 
BASE_RISK_PCT = 0.25 
active_targets = {} 
CSV_FILE = "ferrari_flight_data.csv"

# --- TELEMETRY MODULE ---
def log_flight_recorder(data_dict):
    file_exists = os.path.isfile(CSV_FILE)
    try:
        with open(CSV_FILE, mode='a', newline='') as f:
            fieldnames = ["timestamp", "coin", "action", "price", "roi", "gandalf", "vola_mod", "equity", "vola"]
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            if not file_exists: writer.writeheader()
            writer.writerow(data_dict)
    except: pass

def add_thought(text):
    ts = time.strftime("%H:%M:%S")
    print(f"  🧠 [COUNCIL] {ts} | {text}")

# --- 2. BRAINS ---
def get_market_data(coin):
    try:
        c = info.candles_snapshot(coin, "1m", 40, int(time.time() * 1000))
        if not c or len(c) < 20: return None
        closes = [float(x['c']) for x in c]
        lows = [float(x['l']) for x in c]; highs = [float(x['h']) for x in c]
        sma = statistics.mean(closes[-20:]); std = statistics.stdev(closes[-20:])
        return {
            "price": closes[-1], "lower": sma - (std*2), "upper": sma + (std*2), 
            "volatility": (std/closes[-1])*100, "candles": c, "closes": closes, 
            "lows": lows, "highs": highs
        }
    except: return None

def brain_alpha_technician(d, vola):
    closes = d["closes"]; sma7 = statistics.mean(closes[-7:])
    if vola >= 0.15:
        if d["price"] > sma7: return "LONG (Flow)"
        if d["price"] < sma7: return "SHORT (Flow)"
    else:
        if d["price"] < d["lower"]: return "LONG (Bounce)"
        if d["price"] > d["upper"]: return "SHORT (Bounce)"
    return "WAIT"

def brain_beta_oracle(d):
    closes = d["closes"]; ema8 = statistics.mean(closes[-8:]); ema21 = statistics.mean(closes[-21:])
    return "UP" if ema8 > ema21 else "DOWN"

def brain_gamma_sentinel(coin):
    try:
        l2 = info.l2_snapshot(coin)
        bids = sum([float(x['sz']) for x in l2['levels'][0][:3]])
        asks = sum([float(x['sz']) for x in l2['levels'][1][:3]])
        return "BULLS" if bids > asks else "BEARS"
    except: return "STABLE"

def brain_delta_strategist(d):
    closes = d["closes"]; lows = d["lows"]; highs = d["highs"]
    pole_up = (closes[-1] - closes[-15]) / closes[-15]
    pole_down = (closes[-1] - closes[-15]) / closes[-15]
    if pole_up > 0.005: return "FLAG_UP"
    if pole_down < -0.005: return "FLAG_DOWN"
    last_low = min(lows[-5:]); prev_low = min(lows[-15:-5])
    if abs(last_low - prev_low) / prev_low < 0.002 and closes[-1] > last_low * 1.001: return "W_PATTERN"
    last_high = max(highs[-5:]); prev_high = max(highs[-15:-5])
    if abs(last_high - prev_high) / prev_high < 0.002 and closes[-1] < last_high * 0.999: return "M_PATTERN"
    return "NONE"

def brain_gandalf_wizard():
    try:
        btc_data = get_market_data("BTC")
        if not btc_data: return "UNKNOWN", 1.0
        closes = btc_data["closes"]; price = btc_data["price"]
        ema20 = statistics.mean(closes[-20:]); ema50 = statistics.mean(closes[-40:])
        vola = btc_data["volatility"]
        
        regime = "GREY_HAVENS"
        risk_modifier = 1.0
        
        if price > ema20 and ema20 > ema50: regime = "THE_DAWN (Bull)"; risk_modifier = 1.2
        elif price < ema20 and ema20 < ema50: regime = "MORDOR (Bear)"; risk_modifier = 0.8
        
        if vola > 0.40: 
            regime = "BALROG (Panic)"; risk_modifier = 0.5 
            
        return regime, risk_modifier
    except: return "UNKNOWN", 1.0

def calculate_physics_targets(d, pattern, side, entry_price, vola, risk_mod):
    closes = d["closes"]
    height = entry_price * (vola / 100) * 2
    if "FLAG" in pattern: height = abs(closes[-1] - closes[-15])
    elif "W_PATTERN" in pattern: height = abs(max(closes[-15:]) - min(closes[-15:]))

    damping = (0.8 if vola > 0.20 else 0.6) * risk_mod
    
    if side == "LONG":
        tp = entry_price + (height * damping * 2.5) 
        sl = entry_price - (height * 0.8) 
    else: 
        tp = entry_price - (height * damping * 2.5)
        sl = entry_price + (height * 0.8)
    return tp, sl

# --- 3. MAIN ENGINE ---
print("🚀 FERRARI V26.0 BLACK BOX RECORDER ONLINE")
print("-" * 65)

while True:
    try:
        mids = info.all_mids()
        state = info.user_state(addr)
        equity = float(state["marginSummary"]["accountValue"])
        if START_EQUITY == 0: START_EQUITY = equity
        raw_pos = [p for p in state["assetPositions"] if float(p["position"]["szi"]) != 0]
        
        wizard_regime, wizard_mod = brain_gandalf_wizard()
        
        ts = time.strftime("%H:%M:%S")
        print(f"\n--- [ HUD UPDATE {ts} ] ---")
        print(f"🧙‍♂️ GANDALF: {wizard_regime:<15} | Risk Mod: {wizard_mod:.2f}x")
        print(f"💰 Equity: ${equity:.2f} | Net: {((equity-START_EQUITY)/START_EQUITY)*100:+.2f}%")
        
        current_active_coins = []
        if raw_pos:
            print(f"📡 ACTIVE POSITIONS ({len(raw_pos)}/{MAX_POSITIONS}):")
            for p in raw_pos:
                pos = p["position"]; coin = pos["coin"]; sz = float(pos["szi"])
                entry = float(pos["entryPx"]); curr = float(mids[coin])
                roi = (curr - entry) / entry if sz > 0 else (entry - curr) / entry
                current_active_coins.append(coin)
                
                # Retro-Fit
                if coin not in active_targets:
                    d_retro = get_market_data(coin)
                    if d_retro:
                        vola = d_retro['volatility']
                        side = "LONG" if sz > 0 else "SHORT"
                        tp, sl = calculate_physics_targets(d_retro, "RETRO", side, entry, vola, wizard_mod)
                        active_targets[coin] = {"tp": tp, "sl": sl}
                        add_thought(f"⚙️ RETRO-FIT: {coin}")
                
                targets = active_targets.get(coin, {"tp": 0, "sl": 0})
                tp_price = targets["tp"]; sl_price = targets["sl"]

                # --- MAGMA LOCK LOGIC ---
                new_sl = sl_price
                lock_msg = ""
                
                if wizard_regime != "BALROG (Panic)":
                    if sz > 0:
                        if roi > 0.03: 
                            active_targets[coin]["tp"] = entry * 1.50; new_sl = max(sl_price, entry * 1.02); lock_msg = "MOONBAG"
                        elif roi > 0.015: new_sl = max(sl_price, entry * 1.01); lock_msg = "LOCK"
                        elif roi > 0.0075: new_sl = max(sl_price, entry * 1.001); lock_msg = "RISK_FREE"
                    elif sz < 0:
                        if roi > 0.03: active_targets[coin]["tp"] = entry * 0.50; new_sl = min(sl_price, entry * 0.98); lock_msg = "MOONBAG"
                        elif roi > 0.015: new_sl = min(sl_price, entry * 0.99); lock_msg = "LOCK"
                        elif roi > 0.0075: new_sl = min(sl_price, entry * 0.999); lock_msg = "RISK_FREE"
                
                if new_sl != sl_price:
                    active_targets[coin]["sl"] = new_sl
                    add_thought(f"🔒 MAGMA {lock_msg} -> New SL: {new_sl:.4f}")
                    sl_price = new_sl

                side_str = 'LONG' if sz > 0 else 'SHORT'
                print(f"  ∟ {coin:<5} {side_str:<5} ROI:{roi*100:>+6.2f}% | TP: {tp_price:.4f} | SL: {sl_price:.4f}")
                
                # LOG TELEMETRY
                log_flight_recorder({
                    "timestamp": ts, "coin": coin, "action": "HOLD", "price": curr,
                    "roi": f"{roi:.4f}", "gandalf": wizard_regime, "vola_mod": wizard_mod,
                    "equity": f"{equity:.2f}"
                })

                # --- EXIT LOGIC ---
                exit_reason = None
                if tp_price > 0:
                    if sz > 0: 
                        if curr >= tp_price: exit_reason = "TARGET_HIT"
                        elif curr <= sl_price: exit_reason = "STOP_HIT"
                    else: 
                        if curr <= tp_price: exit_reason = "TARGET_HIT"
                        elif curr >= sl_price: exit_reason = "STOP_HIT"
                
                if wizard_regime == "BALROG (Panic)" and roi < -0.005: exit_reason = "BALROG_PANIC"
                if roi < -0.012: exit_reason = "HARD_STOP"

                if exit_reason:
                    add_thought(f"🛑 EXIT: {coin} ({exit_reason})")
                    log_flight_recorder({"timestamp": ts, "coin": coin, "action": exit_reason, "price": curr, "roi": roi, "gandalf": wizard_regime})
                    exch.market_close(coin)

        else:
            print("📡 STATUS: No active positions. Searching...")
            active_targets = {}

        if len(current_active_coins) < MAX_POSITIONS:
            candidate = random.choice([c for c in TARGET_COINS if c not in current_active_coins])
            d = get_market_data(candidate)
            if d:
                vola = d['volatility']
                s_a = brain_alpha_technician(d, vola)
                s_b = brain_beta_oracle(d)
                s_c = brain_gamma_sentinel(candidate)
                s_d = brain_delta_strategist(d)
                
                print(f"🔍 SCAN: {candidate:<5} | Vola:{vola:.2f}% | A:{s_a} | B:{s_b} | G:{s_c} | D:{s_d}")
                
                go_long = (("LONG" in s_a and s_b == "UP") or s_d in ["FLAG_UP", "W_PATTERN"]) and s_c == "BULLS"
                go_short = (("SHORT" in s_a and s_b == "DOWN") or s_d in ["FLAG_DOWN", "M_PATTERN"]) and s_c == "BEARS"
                if wizard_regime == "MORDOR (Bear)" and go_long and s_d == "NONE": go_long = False
                if wizard_regime == "THE_DAWN (Bull)" and go_short and s_d == "NONE": go_short = False

                if (go_long or go_short) and vola < 0.25:
                    side = "LONG" if go_long else "SHORT"
                    base_scaler = 1.0 if vola < 0.20 else 0.5
                    final_scaler = base_scaler * wizard_mod 
                    size = ((equity * BASE_RISK_PCT * final_scaler) * LEVERAGE) / d["price"]
                    tp, sl = calculate_physics_targets(d, s_d, side, d["price"], vola, wizard_mod)
                    active_targets[candidate] = {"tp": tp, "sl": sl}
                    add_thought(f"🚀 ENTRY {side}: {candidate} (Mod:{wizard_mod}x)")
                    
                    log_flight_recorder({
                        "timestamp": ts, "coin": candidate, "action": f"ENTRY_{side}", 
                        "price": d["price"], "gandalf": wizard_regime, "vola": f"{vola:.2f}"
                    })
                    
                    exch.market_open(candidate, go_long, round(size, 1), d["price"], 0.01)
                    time.sleep(2)

        time.sleep(10)
    except Exception as e:
        print(f"⚠️ Error: {str(e)[:40]}")
        time.sleep(20)
