""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics

class FerrariV44:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        self.paper_balance = 97.02
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.memory_length = 30
        self.price_history = []
        
        self.target_z = -1.2
        self.max_inventory = 15
        self.last_buy_time = 0
        self.trade_size = 3.0

        self.preload_data()
        print(f"🏎️ FERRARI V4.4 STEALTH ACTIVE. Kassa: ${self.paper_balance:.2f}")

    def preload_data(self):
        print("📥 Ladataan historiamuisti...", end="", flush=True)
        try:
            end = int(time.time() * 1000)
            start = end - (60 * 60 * 1000)
            res = requests.post(self.info_url, headers=self.headers, json={
                "type": "candleSnapshot", 
                "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": end}
            }, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                self.price_history = [float(c['c']) for c in data][-self.memory_length:]
                print(f" VALMIS ({len(self.price_history)} pistettä)")
            else:
                print(f" VIRHE: HTTP {res.status_code}")
        except Exception as e:
            print(f" VIRHE: {e}")

    def get_market_data(self):
        try:
            res_mids = requests.post(self.info_url, headers=self.headers, json={"type": "allMids"}, timeout=5)
            if res_mids.status_code != 200: return 0, []
            
            h_price = float(res_mids.json().get('HYPE', 0))
            res_trades = requests.post(self.info_url, headers=self.headers, json={"type": "marketTrades", "coin": "HYPE"}, timeout=5)
            return h_price, res_trades.json() if res_trades.status_code == 200 else []
        except: return 0, []

    def calculate_whale_delta(self, trades):
        if not trades: return 1.0
        buys = sum(float(t['sz']) for t in trades if t['side'] == 'B')
        sells = sum(float(t['sz']) for t in trades if t['side'] == 'S')
        return buys / sells if sells > 0 else 2.0

    def run(self):
        print("-" * 115)
        try:
            while True:
                h_price, trades = self.get_market_data()
                if h_price == 0:
                    print("⚠️ Yhteys pätkii (Check internet/Proxy)...")
                    time.sleep(3)
                    continue
                
                self.price_history.append(h_price)
                if len(self.price_history) > self.memory_length: self.price_history.pop(0)
                if len(self.price_history) < 5: continue

                mean = statistics.mean(self.price_history)
                stdev = statistics.stdev(self.price_history)
                z_score = (h_price - mean) / stdev if stdev > 0 else 0
                
                target_price = mean + (self.target_z * stdev)
                dist_pct = ((h_price - target_price) / h_price) * 100
                delta = self.calculate_whale_delta(trades)
                
                mode = "READY"
                if delta < 0.5: mode = "WHALE"
                
                time_since_last = time.time() - self.last_buy_time
                cool = max(0, int(45 - time_since_last))

                if z_score <= self.target_z and mode == "READY" and cool == 0:
                    self.paper_balance -= self.trade_size
                    self.paper_inventory += 1
                    self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + h_price) / self.paper_inventory
                    self.last_buy_time = time.time()
                    print(f"\n🚀 [ENTRY] @ {h_price:.3f}\n")

                elif self.paper_inventory > 0:
                    profit = (h_price - self.avg_entry) / self.avg_entry
                    if profit >= 0.008 or z_score > 2.5:
                        self.paper_balance += (self.paper_inventory * self.trade_size) * (1 + profit)
                        print(f"\n💰 [EXIT] @ {h_price:.3f} (+{profit*100:.2f}%)\n")
                        self.paper_inventory = 0
                        self.avg_entry = 0

                equity = self.paper_balance + (self.paper_inventory * 3)
                print(f"HYPE:{h_price:.3f} | TARGET:{target_price:.3f} ({dist_pct:+.2f}%) | Z:{z_score:+.2f} | D:{delta:.1f} | {mode} | 💰${equity:.2f}")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🏁 Stage 4.4 pysäytetty.")

if __name__ == "__main__":
    FerrariV44().run()
