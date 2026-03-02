""" Technical implementation for Hummingbot Gateway V2.1. """
import requests, time, statistics, datetime, math

class FerrariV50:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        # Jatketaan kassan tilanteesta (Voiton jälkeen $97.16)
        self.paper_balance = 97.16
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.price_history = []
        self.target_z = -1.3
        self.base_size = 3.0
        self.max_inv = 15
        self.last_buy_time = 0

        self.preload_data()

    def preload_data(self):
        try:
            end = int(time.time() * 1000)
            start = end - (60 * 60 * 1000)
            res = requests.post(self.info_url, headers=self.headers, json={
                "type": "candleSnapshot", "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": end}
            }, timeout=10).json()
            self.price_history = [float(c['c']) for c in res][-30:]
        except: self.price_history = []

    def get_market_data(self):
        try:
            res_mids = requests.post(self.info_url, headers=self.headers, json={"type": "allMids"}, timeout=5).json()
            h_price = float(res_mids.get('HYPE', 0))
            return h_price
        except: return 0

    def calculate_rich_fuel(self, z):
        deviation = abs(z) - abs(self.target_z)
        multiplier = math.exp(deviation * 0.4)
        return min(self.base_size * multiplier, 12.0)

    def run(self):
        print(f"🏎️  FERRARI V5.0 SCROLLING TELEMETRY | BALANCE: ${self.paper_balance:.2f}")
        print("-" * 100)
        
        try:
            while True:
                h_price = self.get_market_data()
                if h_price == 0:
                    time.sleep(2)
                    continue
                
                self.price_history.append(h_price)
                if len(self.price_history) > 30: self.price_history.pop(0)
                
                mean = statistics.mean(self.price_history)
                stdev = statistics.stdev(self.price_history)
                z = (h_price - mean) / stdev if stdev > 0 else 0
                
                now = datetime.datetime.now().strftime("%H:%M:%S")
                float_pnl = (h_price - self.avg_entry) / self.avg_entry * (self.paper_inventory * self.base_size) if self.paper_inventory > 0 else 0
                equity = self.paper_balance + (self.paper_inventory * self.base_size) + float_pnl
                
                # --- EXIT ---
                if self.paper_inventory > 0 and ((h_price > self.avg_entry and z > 1.3) or (float_pnl / (self.paper_inventory*3) >= 0.01)):
                    profit_pct = (h_price - self.avg_entry) / self.avg_entry * 100
                    print(f"\n[{now}] 💰 [EXIT] @ {h_price:.3f} | Profit: ${float_pnl:.2f} ({profit_pct:+.2f}%)\n")
                    self.paper_balance += (self.paper_inventory * self.base_size) + float_pnl
                    self.paper_inventory = 0
                    self.avg_entry = 0

                # --- ENTRY ---
                elif z <= self.target_z and (time.time() - self.last_buy_time > 40) and self.paper_inventory < self.max_inv:
                    size = self.calculate_rich_fuel(z)
                    if self.paper_balance >= size:
                        self.paper_balance -= size
                        self.paper_inventory += 1
                        self.avg_entry = ((self.paper_inventory-1) * self.avg_entry + h_price) / self.paper_inventory
                        self.last_buy_time = time.time()
                        print(f"\n[{now}] 🔥 [ENTRY] @ {h_price:.3f} | Size: ${size:.2f} | Z: {z:.2f}\n")

                # LOGGING (Data Juoksee)
                pnl_color = "🟢" if float_pnl >= 0 else "🔴"
                inv_status = f"[{self.paper_inventory}/{self.max_inv}]"
                
                # Visual trigger hint
                hint = "⬅️ BUY SOON" if z < -1.0 else ""
                if z > 1.0 and self.paper_inventory > 0: hint = "➡️ SELL SOON"
                
                print(f"[{now}] HYPE:{h_price:.3f} | Z:{z:+.2f} | AVG:{self.avg_entry:.3f} | PnL:{pnl_color}${float_pnl:+.2f} | {inv_status} | 💎${equity:.2f} {hint}")
                
                time.sleep(1)
        except KeyboardInterrupt: pass

if __name__ == "__main__": FerrariV50().run()
