""" Technical implementation for Hummingbot Gateway V2.1. """
import requests, time, statistics, math, datetime, sys

class StatisticsEngine:
    """ Stealth Math Library - Pure Python implementation of complex stats """
    
    @staticmethod
    def calculate_rsi(prices, period=14):
        if len(prices) < period + 1: return 50.0
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d for d in deltas if d > 0]
        losses = [abs(d) for d in deltas if d < 0]
        
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0
        
        if avg_loss == 0: return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_vwap(prices, volumes):
        if not prices or not volumes: return 0
        total_pv = sum(p * v for p, v in zip(prices, volumes))
        total_vol = sum(volumes)
        return total_pv / total_vol if total_vol > 0 else prices[-1]

    @staticmethod
    def calculate_correlation(x, y):
        # Pearson correlation
        n = len(x)
        if n != len(y) or n < 2: return 0
        mu_x, mu_y = statistics.mean(x), statistics.mean(y)
        std_x, std_y = statistics.stdev(x), statistics.stdev(y)
        if std_x == 0 or std_y == 0: return 0
        
        covariance = sum((xi - mu_x) * (yi - mu_y) for xi, yi in zip(x, y)) / (n - 1)
        return covariance / (std_x * std_y)

    @staticmethod
    def calculate_skew_kurt(data):
        # 3rd & 4th moments for risk analysis
        n = len(data)
        if n < 4: return 0, 0
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        if std == 0: return 0, 0
        
        skew = sum(((x - mean) / std) ** 3 for x in data) / n
        kurt = sum(((x - mean) / std) ** 4 for x in data) / n - 3
        return skew, kurt

class FerrariV60:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        
        # 🏎️ ENGINE STATE
        self.paper_balance = 97.16
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.max_inv = 15
        self.base_size = 3.0
        self.last_buy_time = 0
        
        # 🧠 MEMORY BANKS
        self.history_limit = 50
        self.h_prices = []
        self.h_volumes = []
        self.b_prices = [] # BTC Correlation memory
        
        # 🛡️ RISK PARAMETERS
        self.target_z = -1.4       # Strict base
        self.rsi_limit = 38        # Only buy oversold
        self.max_correlation = 0.92 # Don't buy if purely following BTC dump
        
        self.preload_data()

    def get_data(self, payload):
        try:
            res = requests.post(self.info_url, headers=self.headers, json=payload, timeout=5)
            return res.json() if res.status_code == 200 else None
        except: return None

    def preload_data(self):
        print("📥 Ladataan 'Fusion Core' dataa (HYPE + BTC)...", end="", flush=True)
        try:
            now = int(time.time() * 1000)
            start = now - (120 * 60 * 1000) # 2h historiaa
            
            # HYPE Data
            h_res = self.get_data({"type": "candleSnapshot", "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": now}})
            # BTC Data (Correlation)
            b_res = self.get_data({"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1m", "startTime": start, "endTime": now}})
            
            if h_res and b_res:
                # Synkronoidaan pituudet
                min_len = min(len(h_res), len(b_res), self.history_limit)
                self.h_prices = [float(c['c']) for c in h_res[-min_len:]]
                self.h_volumes = [float(c['v']) for c in h_res[-min_len:]]
                self.b_prices = [float(c['c']) for c in b_res[-min_len:]]
                print(f" VALMIS ({min_len} kynttilää).")
            else:
                print(" VIRHE.")
        except Exception as e: print(f" VIRHE: {e}")

    def run(self):
        print(f"🏎️  FERRARI V6.0 FUSION CORE | MULTI-VARIABLE ANALYSIS ACTIVE")
        print("-" * 120)
        
        try:
            while True:
                # 1. Fetch Live Data
                mids = self.get_data({"type": "allMids"})
                trades = self.get_data({"type": "marketTrades", "coin": "HYPE"})
                
                if not mids: 
                    time.sleep(2)
                    continue
                
                h_price = float(mids.get('HYPE', 0))
                b_price = float(mids.get('BTC', 0))
                
                # Estimate volume from trades (Snapshot only gives volume on close)
                vol_now = sum(float(t['sz']) for t in trades) if trades else 0.0
                
                # 2. Update Memory
                self.h_prices.append(h_price)
                self.h_volumes.append(vol_now)
                self.b_prices.append(b_price)
                
                if len(self.h_prices) > self.history_limit:
                    self.h_prices.pop(0)
                    self.h_volumes.pop(0)
                    self.b_prices.pop(0)

                # 3. 🧮 RUN STATISTICS ENGINE
                se = StatisticsEngine
                vwap = se.calculate_vwap(self.h_prices, self.h_volumes)
                rsi = se.calculate_rsi(self.h_prices)
                corr = se.calculate_correlation(self.h_prices, self.b_prices)
                skew, kurt = se.calculate_skew_kurt(self.h_prices)
                
                # BBW (Bollinger Band Width)
                stdev = statistics.stdev(self.h_prices)
                mean = statistics.mean(self.h_prices)
                # Z-Score based on VWAP (Smart Z) instead of simple mean
                z_vwap = (h_price - vwap) / stdev if stdev > 0 else 0
                
                # 4. 🧠 FUSION LOGIC GATES
                # Dynamic Z requirement based on Risk (Skew/Kurt)
                required_z = self.target_z
                if skew < -1.0 or kurt > 3.0: required_z -= 0.5 # Vaadi halvempi hinta jos riski iso
                
                gate_z = z_vwap <= required_z
                gate_rsi = rsi <= self.rsi_limit
                gate_corr = corr < self.max_correlation # Älä osta jos seuraa sokeasti BTC-romahdusta
                
                now = datetime.datetime.now().strftime("%H:%M:%S")
                
                # PnL Calc
                float_pnl = 0
                if self.paper_inventory > 0:
                    float_pnl = (h_price - self.avg_entry) / self.avg_entry * (self.paper_inventory * self.base_size)

                # --- ENTRY ---
                cooldown = (time.time() - self.last_buy_time > 45)
                if gate_z and gate_rsi and gate_corr and cooldown and self.paper_inventory < self.max_inv:
                    # Dynamic Sizing based on "Fusion Score"
                    fusion_score = abs(z_vwap) + (100-rsi)/100
                    size = min(self.base_size * fusion_score, 12.0)
                    
                    if self.paper_balance >= size:
                        self.paper_balance -= size
                        self.paper_inventory += 1
                        prev_val = (self.paper_inventory-1) * self.avg_entry
                        self.avg_entry = (prev_val + h_price) / self.paper_inventory
                        self.last_buy_time = time.time()
                        print(f"\n[{now}] ☢️ [FUSION BUY] @ {h_price:.3f} | Z:{z_vwap:.2f} | RSI:{rsi:.0f} | Size:${size:.1f}\n")

                # --- EXIT ---
                elif self.paper_inventory > 0:
                    profit_trigger = (float_pnl / (self.paper_inventory*3) >= 0.008)
                    panic_trigger = (z_vwap > 1.5)
                    if profit_trigger or panic_trigger:
                        print(f"\n[{now}] 💰 [EXIT] @ {h_price:.3f} | Profit: ${float_pnl:.2f}\n")
                        self.paper_balance += (self.paper_inventory * self.base_size) + float_pnl
                        self.paper_inventory = 0
                        self.avg_entry = 0

                # --- TELEMETRY ---
                pnl_c = "🟢" if float_pnl >= 0 else "🔴"
                equity = self.paper_balance + (self.paper_inventory * self.base_size) + float_pnl
                
                # Tiivistetty Status-rivi
                status = "WAIT"
                if gate_z: status = "CHEAP"
                if gate_z and gate_rsi: status = "READY"
                
                print(f"[{now}] HYPE:{h_price:.3f} | Z(vwap):{z_vwap:+.2f} | RSI:{rsi:.0f} | Corr:{corr:.2f} | {status} | 💰${equity:.2f} ({pnl_c})")
                
                time.sleep(1)
        except KeyboardInterrupt: pass

if __name__ == "__main__": FerrariV60().run()
