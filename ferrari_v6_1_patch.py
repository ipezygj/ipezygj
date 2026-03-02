""" Technical implementation for Hummingbot Gateway V2.1. """
import requests, time, statistics, math, datetime, sys

class FerrariV61:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        
        self.paper_balance = 97.16
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.max_inv = 15
        self.base_size = 3.0
        self.last_buy_time = 0
        
        self.history_limit = 50
        self.h_prices = []
        self.b_prices = [] 
        
        # 🛡️ PARAMETRIT
        self.target_z = -1.4       
        self.rsi_limit = 38        
        self.max_correlation = 0.90 # Tiukka seula

        self.preload_data()

    def get_data(self, payload):
        try:
            res = requests.post(self.info_url, headers=self.headers, json=payload, timeout=5)
            return res.json() if res.status_code == 200 else None
        except: return None

    def preload_data(self):
        print("📥 Ladataan ja kalibroidaan sensorit...", end="", flush=True)
        try:
            now = int(time.time() * 1000)
            start = now - (120 * 60 * 1000)
            h_res = self.get_data({"type": "candleSnapshot", "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": now}})
            b_res = self.get_data({"type": "candleSnapshot", "req": {"coin": "BTC", "interval": "1m", "startTime": start, "endTime": now}})
            
            if h_res and b_res:
                min_len = min(len(h_res), len(b_res), self.history_limit)
                self.h_prices = [float(c['c']) for c in h_res[-min_len:]]
                self.b_prices = [float(c['c']) for c in b_res[-min_len:]]
                print(f" VALMIS ({min_len} pistettä).")
            else: print(" VIRHE.")
        except: print(" VIRHE.")

    def calculate_rsi(self, prices):
        if len(prices) < 14: return 50
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d for d in deltas if d > 0]
        losses = [abs(d) for d in deltas if d < 0]
        avg_gain = sum(gains) / 14 if gains else 0
        avg_loss = sum(losses) / 14 if losses else 0
        if avg_loss == 0: return 100
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    def calculate_correlation(self, x, y):
        if len(x) != len(y) or len(x) < 2: return 0
        mu_x, mu_y = statistics.mean(x), statistics.mean(y)
        std_x, std_y = statistics.stdev(x), statistics.stdev(y)
        if std_x == 0 or std_y == 0: return 0
        cov = sum((xi - mu_x) * (yi - mu_y) for xi, yi in zip(x, y)) / (len(x) - 1)
        return cov / (std_x * std_y)

    def run(self):
        print(f"🏎️  FERRARI V6.1 SENSOR PATCH ACTIVE")
        print("-" * 110)
        
        try:
            while True:
                mids = self.get_data({"type": "allMids"})
                if not mids: 
                    time.sleep(2)
                    continue
                
                h_price = float(mids.get('HYPE', 0))
                b_price = float(mids.get('BTC', 0))
                
                self.h_prices.append(h_price)
                self.b_prices.append(b_price)
                if len(self.h_prices) > self.history_limit:
                    self.h_prices.pop(0)
                    self.b_prices.pop(0)

                # --- SENSORIT ---
                rsi = self.calculate_rsi(self.h_prices)
                corr = self.calculate_correlation(self.h_prices, self.b_prices)
                
                # Z-SCORE (Standard Mean Z - Luotettavampi silmukassa)
                mean = statistics.mean(self.h_prices)
                stdev = statistics.stdev(self.h_prices)
                z_score = (h_price - mean) / stdev if stdev > 0 else 0
                
                # LOGIC GATES
                gate_z = z_score <= self.target_z
                gate_rsi = rsi <= self.rsi_limit
                gate_corr = corr < self.max_correlation
                
                now = datetime.datetime.now().strftime("%H:%M:%S")
                float_pnl = 0
                if self.paper_inventory > 0:
                    float_pnl = (h_price - self.avg_entry) / self.avg_entry * (self.paper_inventory * self.base_size)

                # --- ENTRY ---
                cooldown = (time.time() - self.last_buy_time > 45)
                if gate_z and gate_rsi and gate_corr and cooldown and self.paper_inventory < self.max_inv:
                    size = min(self.base_size * (abs(z_score) + 1), 12.0)
                    if self.paper_balance >= size:
                        self.paper_balance -= size
                        self.paper_inventory += 1
                        prev = (self.paper_inventory-1) * self.avg_entry
                        self.avg_entry = (prev + h_price) / self.paper_inventory
                        self.last_buy_time = time.time()
                        print(f"\n[{now}] ☢️ [BUY] @ {h_price:.3f} | Z:{z_score:.2f} | RSI:{rsi:.0f}\n")

                # --- EXIT ---
                elif self.paper_inventory > 0:
                    profit = (float_pnl / (self.paper_inventory*3) >= 0.008)
                    panic = (z_score > 1.8)
                    if profit or panic:
                        print(f"\n[{now}] 💰 [EXIT] @ {h_price:.3f} | Profit: ${float_pnl:.2f}\n")
                        self.paper_balance += (self.paper_inventory * self.base_size) + float_pnl
                        self.paper_inventory = 0
                        self.avg_entry = 0

                # --- TELEMETRY ---
                pnl_c = "🟢" if float_pnl >= 0 else "🔴"
                equity = self.paper_balance + (self.paper_inventory * self.base_size) + float_pnl
                
                status = "WAIT"
                if not gate_corr and rsi < 40: status = "CORR_LOCK" # Näyttää miksi ei osta
                elif gate_z and gate_rsi: status = "READY"
                elif gate_z: status = "CHEAP"
                
                print(f"[{now}] HYPE:{h_price:.3f} | Z:{z_score:+.2f} | RSI:{rsi:.0f} | Corr:{corr:.2f} | {status} | 💰${equity:.2f} ({pnl_c})")
                time.sleep(1)
        except KeyboardInterrupt: pass

if __name__ == "__main__": FerrariV61().run()
