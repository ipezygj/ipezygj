""" Technical implementation for Hummingbot Gateway V2.1. """
import datetime
import json
import os
import requests
import statistics
import time

class FerrariV3Ultimate:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.paper_balance = 100.00
        self.paper_inventory = 0
        self.avg_entry = 0.0
        
        # 🧠 ÄLYKÄS MUISTI
        self.memory_length = 30
        self.price_history = []  # HYPE hinta
        self.btc_history = []    # Markkina-indeksi
        
        # 🏎️ TURBO-PARAMETRIT
        self.base_trigger = -1.2
        self.max_inventory = 15   
        self.last_buy_time = 0
        
        # 📉 TRAILING PROFIT
        self.highest_profit_seen = 0.0
        self.trailing_active = False

        self.preload_history()
        print(f"🏎️ FERRARI V3 ULTIMATE - STAGE 3 ACTIVE. Kassa: ${self.paper_balance:.2f}")

    def preload_history(self):
        try:
            end = int(time.time() * 1000)
            start = end - (60*60*1000)
            r = requests.post(self.info_url, json={
                "type": "candleSnapshot", 
                "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": end}
            }).json()
            for c in r: self.price_history.append(float(c['c']))
            if len(self.price_history) > self.memory_length:
                self.price_history = self.price_history[-self.memory_length:]
        except: pass

    def get_market_data(self):
        try:
            r = requests.post(self.info_url, json={"type": "allMids"}).json()
            return float(r.get('HYPE', 0)), float(r.get('BTC', 0))
        except: return 0, 0

    def calculate_alpha_logic(self, current_price, current_btc):
        self.price_history.append(current_price)
        self.btc_history.append(current_btc)
        if len(self.price_history) > self.memory_length: self.price_history.pop(0)
        if len(self.btc_history) > 5: self.btc_history.pop(0)
        
        if len(self.price_history) < 10: return False, 0, "INIT", 0

        mean = statistics.mean(self.price_history)
        stdev = statistics.stdev(self.price_history)
        z_score = (current_price - mean) / stdev if stdev > 0 else 0
        
        # TURBO 1: Momentum Brake
        momentum = current_price - self.price_history[-3] if len(self.price_history) > 3 else 0
        is_crashing = momentum < -(stdev * 0.5) if stdev > 0 else False
        
        # TURBO 2: Alpha Correlation
        btc_change = (current_btc - self.btc_history[0]) / self.btc_history[0] if len(self.btc_history) > 1 else 0
        hype_change = (current_price - self.price_history[-5]) / self.price_history[-5] if len(self.price_history) > 5 else 0
        is_market_noise = btc_change < -0.0005 and hype_change > btc_change 

        # TURBO 3: Precision Fuel Injection
        if z_score < -3.0: weight = 3.0 
        elif z_score < -2.0: weight = 1.5 
        else: weight = 1.0 
        
        entry_signal = (z_score <= self.base_trigger) and not is_crashing and not is_market_noise
        
        mode = "SNIPER"
        if is_crashing: mode = "BRAKE"
        elif is_market_noise: mode = "SYNC"
        
        return entry_signal, weight, mode, z_score

    def run(self):
        print(f"🏁 ALPHA-ANALYYSI KÄYNNISSÄ. ODOTETAAN DATA-AALTOA.")
        print("-" * 105)
        
        try:
            while True:
                h_price, b_price = self.get_market_data()
                if h_price == 0: continue
                
                entry_sig, weight, mode, z_score = self.calculate_alpha_logic(h_price, b_price)
                
                time_since_last = time.time() - self.last_buy_time
                cooldown = 45 if mode != "BRAKE" else 120
                is_cool = time_since_last > cooldown

                # OSTO
                if entry_sig and self.paper_inventory < self.max_inventory and is_cool:
                    buy_amount = 3.0 * weight
                    self.paper_balance -= buy_amount
                    self.paper_inventory += 1
                    self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + h_price) / self.paper_inventory
                    self.last_buy_time = time.time()
                    print(f"🚀 [ALPHA BUY] @ {h_price:.3f} | Z: {z_score:.2f} | Panos: ${buy_amount:.1f} | Mode: {mode}")

                # MYYNTI
                elif self.paper_inventory > 0:
                    profit = (h_price - self.avg_entry) / self.avg_entry
                    
                    if profit >= 0.008 and not self.trailing_active:
                        self.trailing_active = True
                        self.highest_profit_seen = profit
                    
                    if self.trailing_active:
                        if profit > self.highest_profit_seen: self.highest_profit_seen = profit
                        if profit < (self.highest_profit_seen - 0.002):
                            profit_usd = (self.paper_inventory * 3.0) * profit
                            self.paper_balance += (self.paper_inventory * 3.0) + profit_usd
                            print(f"💰 [TRAILED SELL] @ {h_price:.3f} (+{profit*100:.2f}%)")
                            self.paper_inventory = 0
                            self.avg_entry = 0
                            self.trailing_active = False
                    
                    elif z_score > 2.5 and profit > 0.001:
                        self.paper_balance += (self.paper_inventory * 3.0) * (1 + profit)
                        print(f"⚡ [FLASH SELL] @ {h_price:.3f} (Z-Spike)")
                        self.paper_inventory = 0
                        self.avg_entry = 0

                total_equity = self.paper_balance + (self.paper_inventory * 3.0)
                pnl = ((h_price - self.avg_entry) / self.avg_entry * 100) if self.avg_entry > 0 else 0
                print(f"HYPE:{h_price:.3f} | BTC:{b_price:.0f} | 💰${total_equity:.2f} | Z:{z_score:.2f} | {mode} | PnL:{pnl:.2f}%")
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🏁 Stage 3 pysäytetty.")

if __name__ == "__main__":
    FerrariV3Ultimate().run()
