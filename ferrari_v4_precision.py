""" Technical implementation for Hummingbot Gateway V2.1. """
import datetime
import json
import os
import requests
import statistics
import time

class FerrariV4Precision:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.paper_balance = 100.00
        self.paper_inventory = 0
        self.avg_entry = 0.0
        
        # 🧠 ÄLYKÄS MUISTI (Extended for Regime Filter)
        self.memory_length = 50
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

        self.preload_history()
        print(f"🏎️ FERRARI V4 PRECISION - STAGE 4 ACTIVE. Kassa: ${self.paper_balance:.2f}")

    def preload_history(self):
        try:
            end = int(time.time() * 1000)
            start = end - (120*60*1000)
            r = requests.post(self.info_url, json={
                "type": "candleSnapshot", 
                "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": end}
            }).json()
            for c in r: self.price_history.append(float(c['c']))
            if len(self.price_history) > self.memory_length:
                self.price_history = self.price_history[-self.memory_length:]
        except Exception: pass

    def get_market_data(self):
        """ Hakee hinnan, fundingin ja orderbookin yhdellä tai useammalla kutsulla """
        try:
            mids = requests.post(self.info_url, json={"type": "allMids"}).json()
            meta = requests.post(self.info_url, json={"type": "metaAndAssetCtxs"}).json()
            l2 = requests.post(self.info_url, json={"type": "l2Book", "coin": "HYPE"}).json()
            
            # Etsi HYPE funding rate
            funding = 0.0
            for i, asset in enumerate(meta[0]['universe']):
                if asset['name'] == 'HYPE':
                    funding = float(meta[1][i]['funding'])
                    break
                    
            return float(mids.get('HYPE', 0)), float(mids.get('BTC', 0)), funding, l2
        except Exception: return 0, 0, 0, None

    def calculate_v4_logic(self, h_price, b_price, funding, l2):
        self.price_history.append(h_price)
        self.btc_history.append(b_price)
        if len(self.price_history) > self.memory_length: self.price_history.pop(0)
        if len(self.btc_history) > 10: self.btc_history.pop(0)
        
        if len(self.price_history) < 20: return False, 0, "INIT", 0

        mean = statistics.mean(self.price_history)
        stdev = statistics.stdev(self.price_history)
        z_score = (h_price - mean) / stdev if stdev > 0 else 0
        
        # --- 1. ORDER BOOK IMBALANCE (Seinä-sensori) ---
        # Lasketaan bid vs ask painotus 0.5% säteellä mid-hinnasta
        bids_sum = sum(float(b['sz']) for b in l2['levels'][0][:5]) # Top 5 ostotasoa
        asks_sum = sum(float(a['sz']) for a in l2['levels'][1][:5]) # Top 5 myyntitasoa
        imbalance = bids_sum / asks_sum if asks_sum > 0 else 1.0
        wall_support = imbalance > 1.2 # Ostoja oltava 20% enemmän kuin myyntejä

        # --- 2. FUNDING-AWARE ADJUSTMENT ---
        # Jos funding on positiivinen, olemme herkempiä ostamaan (saamme palkkion)
        funding_adj = 0.1 if funding > 0 else -0.2
        effective_trigger = self.base_trigger + funding_adj

        # --- 3. VOLATILITY REGIME (Trend vs Range) ---
        # Lasketaan hinnan "suuntaus". Jos hinta on jyrkässä trendissä alas, vältetään.
        short_mean = statistics.mean(self.price_history[-5:])
        long_mean = statistics.mean(self.price_history[-20:])
        is_death_trend = short_mean < long_mean * 0.998 # Selkeä laskutrendi

        # Yhdistetty päätös
        mode = "CRUISE"
        if is_death_trend: mode = "TREND_WAIT"
        elif not wall_support: mode = "NO_WALL"
        elif funding < -0.0001: mode = "HIGH_COST"

        entry_signal = (z_score <= effective_trigger) and wall_support and not is_death_trend
        
        # Painotus dipin syvyyden mukaan
        weight = 1.0
        if z_score < -3.0: weight = 2.5
        
        return entry_signal, weight, mode, z_score

    def run(self):
        print(f"🏁 FERRARI PRECISION KÄYNNISSÄ. ANALYSOIDAAN SEINIÄ JA TRENDEJÄ.")
        print("-" * 110)
        
        try:
            while True:
                h_price, b_price, funding, l2 = self.get_market_data()
                if h_price == 0 or not l2: continue
                
                entry_sig, weight, mode, z_score = self.calculate_v4_logic(h_price, b_price, funding, l2)
                
                time_since_last = time.time() - self.last_buy_time
                cooldown = 60 if mode != "CRUISE" else 30
                is_cool = time_since_last > cooldown

                # OSTO
                if entry_sig and self.paper_inventory < self.max_inventory and is_cool:
                    buy_amount = self.trade_size * weight
                    self.paper_balance -= buy_amount
                    self.paper_inventory += 1
                    self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + h_price) / self.paper_inventory
                    self.last_buy_time = time.time()
                    print(f"🚀 [PRECISION BUY] @ {h_price:.3f} | Z:{z_score:.2f} | Wall:{mode}")

                # MYYNTI (Trailing Active)
                elif self.paper_inventory > 0:
                    profit = (h_price - self.avg_entry) / self.avg_entry
                    if profit >= 0.008 and not self.trailing_active:
                        self.trailing_active = True
                        self.highest_profit_seen = profit
                    
                    if self.trailing_active:
                        if profit > self.highest_profit_seen: self.highest_profit_seen = profit
                        if profit < (self.highest_profit_seen - 0.002):
                            profit_usd = (self.paper_inventory * self.trade_size) * profit
                            self.paper_balance += (self.paper_inventory * self.trade_size) + profit_usd
                            print(f"💰 [TRAILED SELL] @ {h_price:.3f} (+{profit*100:.2f}%)")
                            self.paper_inventory = 0
                            self.avg_entry = 0
                            self.trailing_active = False

                total_equity = self.paper_balance + (self.paper_inventory * self.trade_size)
                print(f"HYPE:{h_price:.3f} | Z:{z_score:.2f} | Fund:{funding:.6f} | Mode:{mode} | 💰${total_equity:.2f}")
                
                time.sleep(2)
        except KeyboardInterrupt:
            print("\n🏁 Stage 4 pysäytetty.")

if __name__ == "__main__":
    FerrariV4Precision().run()
