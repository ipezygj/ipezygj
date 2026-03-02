""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics

class FerrariV41:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.paper_balance = 97.02
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.memory_length = 30
        self.price_history = []
        self.btc_history = []
        
        # 🏎️ PARAMETRIT
        self.base_trigger = -1.2
        self.max_inventory = 15
        self.last_buy_time = 0
        self.trade_size = 3.0
        
        # 📉 TRAILING PROFIT
        self.highest_profit_seen = 0.0
        self.trailing_active = False

        print(f"🏎️ FERRARI V4.1 WHALE HUNTER ACTIVE. Kassa: ${self.paper_balance:.2f}")

    def get_market_data(self):
        try:
            mids = requests.post(self.info_url, json={"type": "allMids"}).json()
            # Haetaan tuoreimmat toteutuneet kaupat (Volume Delta)
            trades = requests.post(self.info_url, json={"type": "marketTrades", "coin": "HYPE"}).json()
            return float(mids.get('HYPE', 0)), float(mids.get('BTC', 0)), trades
        except: return 0, 0, []

    def calculate_whale_delta(self, trades):
        """ Laskee onko myyntipaine (valaat) ylivoimainen """
        if not trades: return 1.0
        buy_vol = sum(float(t['sz']) for t in trades if t['side'] == 'B')
        sell_vol = sum(float(t['sz']) for t in trades if t['side'] == 'S')
        return buy_vol / sell_vol if sell_vol > 0 else 2.0

    def run(self):
        print(f"🏁 ANALYSOIDAAN VALAITA JA MOMENTUMIA.")
        print("-" * 100)
        
        try:
            while True:
                h_price, b_price, trades = self.get_market_data()
                if h_price == 0: continue
                
                self.price_history.append(h_price)
                self.btc_history.append(b_price)
                if len(self.price_history) > self.memory_length: self.price_history.pop(0)
                
                if len(self.price_history) < 10: continue

                mean = statistics.mean(self.price_history)
                stdev = statistics.stdev(self.price_history)
                z_score = (h_price - mean) / stdev if stdev > 0 else 0
                
                # SENSORIT
                delta = self.calculate_whale_delta(trades)
                momentum = h_price - self.price_history[-3]
                
                # TILAT
                mode = "SNIPER"
                if momentum < -(stdev * 0.5): mode = "BRAKE"
                elif delta < 0.5: mode = "WHALE_DUMP" # Myyntiä 2x enemmän kuin ostoa
                
                time_since_last = time.time() - self.last_buy_time
                is_cool = time_since_last > 45

                # OSTO-LOGIIKKA (V4.1)
                if z_score <= self.base_trigger and mode == "SNIPER" and is_cool:
                    self.paper_balance -= self.trade_size
                    self.paper_inventory += 1
                    self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + h_price) / self.paper_inventory
                    self.last_buy_time = time.time()
                    print(f"🚀 [WHALE-SAFE BUY] @ {h_price:.3f} | Z:{z_score:.2f} | Delta:{delta:.2f}")

                # MYYNTI (Trailing)
                elif self.paper_inventory > 0:
                    profit = (h_price - self.avg_entry) / self.avg_entry
                    if profit >= 0.008 or z_score > 2.5:
                        self.paper_balance += (self.paper_inventory * self.trade_size) * (1 + profit)
                        print(f"💰 [SMART EXIT] @ {h_price:.3f} (+{profit*100:.2f}%)")
                        self.paper_inventory = 0
                        self.avg_entry = 0

                total_equity = self.paper_balance + (self.paper_inventory * self.trade_size)
                print(f"HYPE:{h_price:.3f} | Z:{z_score:.2f} | Delta:{delta:.2f} | Mode:{mode} | 💰${total_equity:.2f}")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🏁 Pysäytetty.")

if __name__ == "__main__":
    FerrariV41().run()
