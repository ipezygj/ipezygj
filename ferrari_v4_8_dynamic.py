""" Technical implementation for Hummingbot Gateway V2.1. """
import requests, time, statistics, sys, math

class FerrariV48:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"User-Agent": "Mozilla/5.0"}
        # Jatketaan siitä mihin jäit (5 siivua, 97.02 total)
        self.paper_balance = 82.02 
        self.paper_inventory = 5
        self.avg_entry = 29.458
        self.price_history = []
        self.target_z = -1.2
        self.base_size = 3.0
        self.last_buy_time = 0

    def get_data(self, payload):
        try:
            res = requests.post(self.info_url, headers=self.headers, json=payload, timeout=5)
            return res.json() if res.status_code == 200 else None
        except: return None

    def calculate_dynamic_size(self, z_score):
        # Laskee kertoimen: Mitä syvempi dippi, sitä isompi panos
        # Esim: Z=-1.2 -> 1.0x | Z=-3.0 -> 2.5x | Z=-5.0 -> 4.0x
        deviation = abs(z_score)
        multiplier = max(1.0, deviation / abs(self.target_z))
        # Rajoitetaan ettei karata käsistä (Max 4x panos)
        multiplier = min(multiplier, 4.0)
        return self.base_size * multiplier

    def run(self):
        print(f"🚀 FERRARI V4.8 DYNAMIC INJECTION ACTIVE")
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
                z_score = (h_price - mean) / stdev if stdev > 0 else 0
                
                float_pnl = (h_price - self.avg_entry) / self.avg_entry * (self.paper_inventory * self.base_size) if self.paper_inventory > 0 else 0
                real_equity = self.paper_balance + (self.paper_inventory * self.base_size) + float_pnl
                
                # --- EXIT ---
                if self.paper_inventory > 0 and ((float_pnl / (self.paper_inventory * self.base_size) >= 0.008) or (z_score > 1.2)):
                    print(f"\n💰 [EXIT] @ {h_price:.3f} | Profit: ${float_pnl:.2f}\n")
                    self.paper_balance += (self.paper_inventory * self.base_size) + float_pnl
                    self.paper_inventory = 0
                    self.avg_entry = 0

                # --- DYNAAMINEN ENTRY ---
                elif z_score <= self.target_z and (time.time() - self.last_buy_time > 45) and self.paper_inventory < 15:
                    current_size = self.calculate_dynamic_size(z_score)
                    self.paper_balance -= current_size
                    self.paper_inventory += 1
                    # Lasketaan painotettu keskihinta oikein
                    prev_val = (self.paper_inventory - 1) * self.avg_entry
                    self.avg_entry = (prev_val + h_price) / self.paper_inventory
                    self.last_buy_time = time.time()
                    print(f"\n🔥 [DYNAMIC ENTRY] @ {h_price:.3f} | Size: ${current_size:.2f} (Z:{z_score:.2f})\n")

                color = "🟢" if float_pnl >= 0 else "🔴"
                sys.stdout.write(f"\rHYPE:{h_price:.3f} | AVG:{self.avg_entry:.3f} | PnL:{color}${float_pnl:+.2f} | Z:{z_score:+.2f} | INV:{self.paper_inventory} | 💎${real_equity:.2f}   ")
                sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt: print("\n🏁 Pysäytetty.")

if __name__ == "__main__": FerrariV48().run()
