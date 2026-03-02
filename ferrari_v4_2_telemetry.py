""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import os

class FerrariV42:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.paper_balance = 97.02
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.memory_length = 30
        self.price_history = []
        
        # 🏎️ PARAMETRIT
        self.target_z = -1.2
        self.max_inventory = 15
        self.last_buy_time = 0
        self.trade_size = 3.0
        
        self.highest_profit_seen = 0.0
        self.trailing_active = False

        print(f"🏎️ FERRARI V4.2 TELEMETRY ACTIVE. Kassa: ${self.paper_balance:.2f}")

    def get_market_data(self):
        try:
            mids = requests.post(self.info_url, json={"type": "allMids"}).json()
            trades = requests.post(self.info_url, json={"type": "marketTrades", "coin": "HYPE"}).json()
            return float(mids.get('HYPE', 0)), trades
        except: return 0, []

    def calculate_whale_delta(self, trades):
        if not trades: return 1.0
        buy_vol = sum(float(t['sz']) for t in trades if t['side'] == 'B')
        sell_vol = sum(float(t['sz']) for t in trades if t['side'] == 'S')
        return buy_vol / sell_vol if sell_vol > 0 else 2.0

    def run(self):
        print(f"🏁 ODOTETAAN ANALYYSIÄ... (Täyttyy 10 sekunnissa)")
        print("-" * 115)
        
        try:
            while True:
                h_price, trades = self.get_market_data()
                if h_price == 0: continue
                
                self.price_history.append(h_price)
                if len(self.price_history) > self.memory_length: self.price_history.pop(0)
                if len(self.price_history) < 10: 
                    time.sleep(1)
                    continue

                mean = statistics.mean(self.price_history)
                stdev = statistics.stdev(self.price_history)
                z_score = (h_price - mean) / stdev if stdev > 0 else 0
                
                # --- ETÄISYYSAJO (Distance calculation) ---
                target_price = mean + (self.target_z * stdev)
                dist_pct = ((h_price - target_price) / h_price) * 100
                
                delta = self.calculate_whale_delta(trades)
                momentum = h_price - self.price_history[-3]
                
                # Tilat
                mode = "READY"
                if momentum < -(stdev * 0.5): mode = "BRAKE"
                elif delta < 0.5: mode = "WHALE"
                
                time_since_last = time.time() - self.last_buy_time
                cooldown_left = max(0, int(45 - time_since_last))

                # OSTO
                if z_score <= self.target_z and mode == "READY" and cooldown_left == 0:
                    self.paper_balance -= self.trade_size
                    self.paper_inventory += 1
                    self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + h_price) / self.paper_inventory
                    self.last_buy_time = time.time()
                    print(f"\n🚀 [ENTRY] @ {h_price:.3f} | Z:{z_score:.2f} | Delta:{delta:.2f}\n")

                # MYYNTI
                elif self.paper_inventory > 0:
                    profit = (h_price - self.avg_entry) / self.avg_entry
                    if profit >= 0.008 or z_score > 2.5:
                        self.paper_balance += (self.paper_inventory * self.trade_size) * (1 + profit)
                        print(f"\n💰 [EXIT] @ {h_price:.3f} (+{profit*100:.2f}%)\n")
                        self.paper_inventory = 0
                        self.avg_entry = 0

                # --- DASHBOARD (Visual Scannability) ---
                inv_str = f"[{self.paper_inventory}/{self.max_inventory}]"
                dist_str = f"TARGET: {target_price:.3f} ({dist_pct:+.2f}%)"
                cool_str = f"COOL:{cooldown_left}s" if cooldown_left > 0 else "GO!"
                
                print(f"HYPE:{h_price:.3f} | {dist_str} | Z:{z_score:+.2f} | D:{delta:.1f} | {mode} | {cool_str} | 💰${self.paper_balance + (self.paper_inventory*3):.2f}")
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🏁 Telemetria suljettu.")

if __name__ == "__main__":
    FerrariV42().run()
