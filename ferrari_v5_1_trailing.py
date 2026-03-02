""" Technical implementation for Hummingbot Gateway V2.1. """
import datetime
import math
import requests
import statistics
import time

class FerrariV51:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        # Jatketaan kassan tilanteesta ($97.16)
        self.paper_balance = 97.16
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.price_history = []
        self.target_z = -1.3
        self.base_size = 3.0
        self.max_inv = 15
        self.last_buy_time = 0
        
        # 🏎️ TRAILING PARAMETERS
        self.trailing_active = False
        self.highest_pnl_seen = 0.0
        self.activation_threshold = 0.006  # 0.6%
        self.callback_rate = 0.002        # 0.2%

        self.preload_data()

    def preload_data(self):
        try:
            end = int(time.time() * 1000)
            start = end - (60 * 60 * 1000)
            res = requests.post(self.info_url, headers=self.headers, json={
                "type": "candleSnapshot", "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": end}
            }, timeout=10).json()
            self.price_history = [float(c['c']) for c in res][-30:]
        except Exception:
            self.price_history = []

    def get_market_data(self):
        try:
            res_mids = requests.post(self.info_url, headers=self.headers, json={"type": "allMids"}, timeout=5).json()
            return float(res_mids.get('HYPE', 0))
        except Exception:
            return 0

    def calculate_rich_fuel(self, z):
        deviation = abs(z) - abs(self.target_z)
        multiplier = math.exp(deviation * 0.4)
        return min(self.base_size * multiplier, 12.0)

    def run(self):
        print(f"🏎️  FERRARI V5.1 ACTIVE REAR WING | BALANCE: ${self.paper_balance:.2f}")
        print("-" * 110)
        
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
                current_pnl_pct = (h_price - self.avg_entry) / self.avg_entry if self.paper_inventory > 0 else 0
                float_pnl_usd = current_pnl_pct * (self.paper_inventory * self.base_size)
                equity = self.paper_balance + (self.paper_inventory * self.base_size) + float_pnl_usd
                
                mode = "READY"
                hint = ""

                # --- TRAILING LOGIC ---
                if self.paper_inventory > 0:
                    # Aktivointi
                    if current_pnl_pct >= self.activation_threshold and not self.trailing_active:
                        self.trailing_active = True
                        self.highest_pnl_seen = current_pnl_pct
                        print(f"\n[{now}] 💎 [WING ACTIVE] Trailing started at {current_pnl_pct*100:.2f}%\n")
                    
                    if self.trailing_active:
                        mode = "TRAILING"
                        # Päivitä huippu
                        if current_pnl_pct > self.highest_pnl_seen:
                            self.highest_pnl_seen = current_pnl_pct
                        
                        # Tarkista pudotus huipusta
                        if current_pnl_pct < (self.highest_pnl_seen - self.callback_rate):
                            print(f"\n[{now}] 💰 [TRAILING EXIT] @ {h_price:.3f} | Profit: ${float_pnl_usd:.2f}")
                            self.paper_balance += (self.paper_inventory * self.base_size) + float_pnl_usd
                            self.paper_inventory = 0
                            self.avg_entry = 0
                            self.trailing_active = False
                            continue

                    # Z-Flip Exit (Varmistus)
                    elif z > 1.3 and current_pnl_pct > 0.002:
                        print(f"\n[{now}] ⚡ [Z-FLIP EXIT] @ {h_price:.3f} | Z:{z:.2f}")
                        self.paper_balance += (self.paper_inventory * self.base_size) + float_pnl_usd
                        self.paper_inventory = 0
                        self.avg_entry = 0
                        continue

                # --- ENTRY LOGIC ---
                if z <= self.target_z and (time.time() - self.last_buy_time > 40) and self.paper_inventory < self.max_inv:
                    size = self.calculate_rich_fuel(z)
                    if self.paper_balance >= size:
                        self.paper_balance -= size
                        self.paper_inventory += 1
                        self.avg_entry = ((self.paper_inventory-1) * self.avg_entry + h_price) / self.paper_inventory
                        self.last_buy_time = time.time()
                        print(f"\n[{now}] 🔥 [ENTRY] @ {h_price:.3f} | Size: ${size:.2f} | Z: {z:.2f}\n")

                # --- TELEMETRY ---
                pnl_color = "🟢" if float_pnl_usd >= 0 else "🔴"
                if z < -1.0: hint = "⬅️ BUY ZONE"
                if self.trailing_active: hint = f"🔥 TRAILING (Max:{self.highest_pnl_seen*100:.2f}%)"
                
                print(f"[{now}] HYPE:{h_price:.3f} | Z:{z:+.2f} | AVG:{self.avg_entry:.3f} | PnL:{pnl_color}${float_pnl_usd:+.2f} | INV:{self.paper_inventory} | 💰${equity:.2f} {hint}")
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🏁 Stage 5.1 pysäytetty.")

if __name__ == "__main__":
    FerrariV51().run()
