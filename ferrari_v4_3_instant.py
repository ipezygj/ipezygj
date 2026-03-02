""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import os

class FerrariV43:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.paper_balance = 97.02
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.memory_length = 30
        self.price_history = []
        
        self.target_z = -1.2
        self.max_inventory = 15
        self.last_buy_time = 0
        self.trade_size = 3.0

        self.preload_data() # Haetaan data heti
        print(f"🏎️ FERRARI V4.3 INSTANT ACTIVE. Kassa: ${self.paper_balance:.2f}")

    def preload_data(self):
        print("📥 Ladataan historiamuisti (1h)...", end="", flush=True)
        try:
            # Haetaan kynttilädata (snapshot) välittömästi
            end = int(time.time() * 1000)
            start = end - (60 * 60 * 1000)
            r = requests.post(self.info_url, json={
                "type": "candleSnapshot", 
                "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": end}
            }, timeout=10).json()
            
            self.price_history = [float(c['c']) for c in r][-self.memory_length:]
            print(f" VALMIS ({len(self.price_history)} pistettä)")
        except Exception as e:
            print(f" VIRHE: {e}")
            self.price_history = []

    def get_market_data(self):
        try:
            r_mids = requests.post(self.info_url, json={"type": "allMids"}, timeout=5).json()
            h_price = float(r_mids.get('HYPE', 0))
            r_trades = requests.post(self.info_url, json={"type": "marketTrades", "coin": "HYPE"}, timeout=5).json()
            return h_price, r_trades
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
                    print("⚠️ Yhteysvirhe... yritetään uudelleen.")
                    time.sleep(2)
                    continue
                
                self.price_history.append(h_price)
                if len(self.price_history) > self.memory_length: self.price_history.pop(0)

                mean = statistics.mean(self.price_history)
                stdev = statistics.stdev(self.price_history)
                z_score = (h_price - mean) / stdev if stdev > 0 else 0
                
                # Mittarit
                target_price = mean + (self.target_z * stdev)
                dist_pct = ((h_price - target_price) / h_price) * 100
                delta = self.calculate_whale_delta(trades)
                
                # Tilat
                mode = "READY"
                if delta < 0.5: mode = "WHALE"
                
                time_since_last = time.time() - self.last_buy_time
                cool = max(0, int(45 - time_since_last))

                # OSTO
                if z_score <= self.target_z and mode == "READY" and cool == 0:
                    self.paper_balance -= self.trade_size
                    self.paper_inventory += 1
                    self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + h_price) / self.paper_inventory
                    self.last_buy_time = time.time()
                    print(f"\n🚀 [ENTRY] @ {h_price:.3f}\n")

                # MYYNTI
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
            print("\n🏁 Stage 4.3 pysäytetty.")

if __name__ == "__main__":
    FerrariV43().run()
