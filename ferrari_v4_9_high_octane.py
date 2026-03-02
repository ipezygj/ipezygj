""" Technical implementation for Hummingbot Gateway V2.1. """
import requests, time, statistics, sys, math

class FerrariV49:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        # Jatketaan samalla kassalla ($97.02 total)
        self.paper_balance = 82.02 # 5 siivua jo sisällä
        self.paper_inventory = 5
        self.avg_entry = 29.458
        self.price_history = []
        self.target_z = -1.3 # Kiristetään hieman tarkkuutta
        self.base_size = 3.0
        self.max_inv = 15
        self.last_buy_time = 0

    def get_data(self, payload):
        try:
            res = requests.post(self.info_url, headers=self.headers, json=payload, timeout=5)
            return res.json() if res.status_code == 200 else None
        except: return None

    def calculate_rich_fuel(self, z):
        # "Rikas seos": Mitä syvempi Z, sitä eksponentiaalisesti suurempi panos
        # Kaava: Base * e^(|Z|-target)
        deviation = abs(z) - abs(self.target_z)
        multiplier = math.exp(deviation * 0.4) # Hallittu eksponentiaalinen kasvu
        return min(self.base_size * multiplier, 12.0) # Capatty $12.00 per isku

    def run(self):
        print(f"🏎️ FERRARI V4.9 HIGH-OCTANE - BREATHING FREELY")
        # Preload
        candles = self.get_data({"type": "candleSnapshot", "req": {"coin": "HYPE", "interval": "1m", "startTime": int((time.time()-3600)*1000), "endTime": int(time.time()*1000)}})
        if candles: self.price_history = [float(c['c']) for c in candles][-30:]

        try:
            while True:
                mids = self.get_data({"type": "allMids"})
                if not mids: continue
                h_price = float(mids.get('HYPE', 0))
                
                self.price_history.append(h_price)
                if len(self.price_history) > 30: self.price_history.pop(0)
                
                mean = statistics.mean(self.price_history)
                stdev = statistics.stdev(self.price_history)
                z = (h_price - mean) / stdev if stdev > 0 else 0
                
                float_pnl = (h_price - self.avg_entry) / self.avg_entry * (self.paper_inventory * self.base_size) if self.paper_inventory > 0 else 0
                equity = self.paper_balance + (self.paper_inventory * self.base_size) + float_pnl
                
                # --- EXIT (Z-Flip tai TP) ---
                if self.paper_inventory > 0 and ((h_price > self.avg_entry and z > 1.3) or (float_pnl / (self.paper_inventory*3) >= 0.01)):
                    print(f"\n💰 [HIGH-OCTANE EXIT] @ {h_price:.3f} | Profit: ${float_pnl:.2f}\n")
                    self.paper_balance += (self.paper_inventory * self.base_size) + float_pnl
                    self.paper_inventory = 0
                    self.avg_entry = 0

                # --- ENTRY (Rich Fuel Injection) ---
                elif z <= self.target_z and (time.time() - self.last_buy_time > 40) and self.paper_inventory < self.max_inv:
                    size = self.calculate_rich_fuel(z)
                    if self.paper_balance >= size:
                        self.paper_balance -= size
                        self.paper_inventory += 1
                        # Painotettu AVG entry laskenta
                        total_cost = ((self.paper_inventory-1) * self.avg_entry) + h_price
                        self.avg_entry = total_cost / self.paper_inventory
                        self.last_buy_time = time.time()
                        print(f"\n🔥 [RICH INJECTION] @ {h_price:.3f} | Size: ${size:.2f} | Z: {z:.2f}\n")

                color = "🟢" if float_pnl >= 0 else "🔴"
                sys.stdout.write(f"\rHYPE:{h_price:.3f} | AVG:{self.avg_entry:.3f} | PnL:{color}${float_pnl:+.2f} | Z:{z:+.2f} | 💰${equity:.2f}   ")
                sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt: pass

if __name__ == "__main__": FerrariV49().run()
