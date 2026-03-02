""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import sys

class FerrariV46:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
        self.paper_balance = 85.02 # 97.02 - (4 * 3.0)
        self.paper_inventory = 4
        self.avg_entry = 29.472
        self.price_history = []
        self.target_z = -1.2
        self.trade_size = 3.0
        self.last_buy_time = 0

    def get_data(self, payload):
        try:
            res = requests.post(self.info_url, headers=self.headers, json=payload, timeout=5)
            if res.status_code == 200: return res.json()
            else:
                print(f"⚠️ Server Error: {res.status_code}")
                return None
        except Exception as e:
            print(f"⚠️ Connection Error: {e}")
            return None

    def run(self):
        print(f"🚀 FERRARI V4.6 - DIAGNOSTIC START")
        print(f"📥 Ladataan alkudataa...")
        
        # Haetaan vain 10 kynttilää jotta käynnistyy nopeasti
        candles = self.get_data({"type": "candleSnapshot", "req": {"coin": "HYPE", "interval": "1m", "startTime": int((time.time()-3600)*1000), "endTime": int(time.time()*1000)}})
        if candles:
            self.price_history = [float(c['c']) for c in candles][-20:]
            print(f"✅ Historia ladattu: {len(self.price_history)} pistettä.")
        
        print("-" * 110)
        try:
            while True:
                # 1. Hae hinta
                mids = self.get_data({"type": "allMids"})
                if not mids: 
                    time.sleep(2)
                    continue
                
                h_price = float(mids.get('HYPE', 0))
                if h_price == 0: continue
                
                # 2. Päivitä statsit
                self.price_history.append(h_price)
                if len(self.price_history) > 30: self.price_history.pop(0)
                
                mean = statistics.mean(self.price_history)
                stdev = statistics.stdev(self.price_history)
                z_score = (h_price - mean) / stdev if stdev > 0 else 0
                
                # 3. PnL laskenta
                float_pnl = (h_price - self.avg_entry) / self.avg_entry * (self.paper_inventory * self.trade_size)
                real_equity = self.paper_balance + (self.paper_inventory * self.trade_size) + float_pnl
                
                # OSTO (45s jäähy)
                if z_score <= self.target_z and (time.time() - self.last_buy_time > 45):
                    self.paper_balance -= self.trade_size
                    self.paper_inventory += 1
                    self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + h_price) / self.paper_inventory
                    self.last_buy_time = time.time()
                    print(f"\n🔥 [ENTRY] @ {h_price:.3f}\n")

                # MYYNTI
                elif self.paper_inventory > 0 and (h_price - self.avg_entry) / self.avg_entry >= 0.008:
                    print(f"\n💰 [EXIT] @ {h_price:.3f} | Profit: ${float_pnl:.2f}\n")
                    self.paper_balance += (self.paper_inventory * self.trade_size) + float_pnl
                    self.paper_inventory = 0
                    self.avg_entry = 0

                color = "🟢" if float_pnl >= 0 else "🔴"
                sys.stdout.write(f"\rHYPE:{h_price:.3f} | AVG:{self.avg_entry:.3f} | PnL:{color}${float_pnl:+.2f} | Z:{z_score:+.2f} | 💰${real_equity:.2f}   ")
                sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🏁 Sammutettu.")

if __name__ == "__main__":
    FerrariV46().run()
