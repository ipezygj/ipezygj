""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import csv
import os
from datetime import datetime

class FerrariV22:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.log_file = os.path.expanduser("~/my_ferrari/ferrari_trades.csv")
        self.paper_balance = 100.00
        self.paper_inventory = 0
        self.avg_entry = 0.0
        self.memory_length = 20
        self.price_memory = []
        self.base_trigger = -1.0
        self.trade_size = 3.0
        self.max_inventory = 10
        self.last_buy_time = 0
        self.base_cooldown = 45
        
        # Alustetaan lokitiedosto
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Type', 'Coin', 'Price', 'Z-Score', 'Amount', 'Profit_USD', 'Total_Equity'])

        self.preload_history()
        print(f"🧪 FERRARI V2.2 BLACK BOX. Kassa: ${self.paper_balance:.2f}")
        print(f"📁 Logi: {self.log_file}")

    def log_trade(self, t_type, price, z_score, amount, profit=0, equity=0):
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), t_type, "HYPE", price, f"{z_score:.2f}", amount, f"{profit:.4f}", f"{equity:.2f}"])

    def get_market_scan(self):
        """ Vilkaisee muut radat (Market Scanner) """
        try:
            r = requests.post(self.info_url, json={"type": "allMids"}).json()
            # Poimitaan muutama mielenkiintoinen
            targets = ['SOL', 'ETH', 'BTC']
            scan_results = {k: v for k, v in r.items() if k in targets}
            return scan_results
        except: return {}

    def preload_history(self):
        try:
            end = int(time.time() * 1000)
            start = end - (60*60*1000)
            r = requests.post(self.info_url, json={
                "type": "candleSnapshot", 
                "req": {"coin": "HYPE", "interval": "1m", "startTime": start, "endTime": end}
            }).json()
            for c in r: self.price_memory.append(float(c['c']))
            if len(self.price_memory) > self.memory_length:
                self.price_memory = self.price_memory[-self.memory_length:]
        except: pass

    def get_price(self):
        try:
            r = requests.post(self.info_url, json={"type": "allMids"}).json()
            return float(r.get('HYPE', 0))
        except: return 0

    def run(self):
        print(f"\n🏎️  FERRARI V2.2 - RECORDING DATA")
        print("-" * 95)
        
        try:
            while True:
                price = self.get_price()
                if price == 0: continue
                self.price_memory.append(price)
                if len(self.price_memory) > self.memory_length: self.price_memory.pop(0)
                if len(self.price_memory) < 5: continue

                mean = statistics.mean(self.price_memory)
                stdev = statistics.stdev(self.price_memory)
                z_score = (price - mean) / stdev
                volatility_ratio = stdev / mean
                
                # Dynaaminen jäähy
                current_cooldown = self.base_cooldown * (2 if volatility_ratio > 0.0025 else 1)
                time_since_last = time.time() - self.last_buy_time
                cooldown_active = time_since_last < current_cooldown
                
                invested_amount = self.paper_inventory * self.trade_size
                profit_pct = (price - self.avg_entry) / self.avg_entry if self.paper_inventory > 0 else 0
                total_equity = self.paper_balance + invested_amount + (invested_amount * profit_pct)

                # Markkinaskanneri (taustalla)
                scan = self.get_market_scan()
                scan_str = " | ".join([f"{k}:{float(v):.1f}" for k, v in scan.items()])

                print(f"HYPE: {price:.3f} | 💰 ${total_equity:.2f} | Z: {z_score:.2f} | {scan_str}")

                # OSTO
                if z_score <= self.base_trigger and self.paper_inventory < self.max_inventory:
                    if not cooldown_active:
                        print(f"🚀 [BUY] RECORDED @ {price:.3f}")
                        self.paper_balance -= self.trade_size
                        self.paper_inventory += 1
                        if self.avg_entry == 0: self.avg_entry = price
                        else: self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + price) / self.paper_inventory
                        self.last_buy_time = time.time()
                        self.log_trade("BUY", price, z_score, self.trade_size, 0, total_equity)

                # MYYNTI
                elif self.paper_inventory > 0:
                    profit = (price - self.avg_entry) / self.avg_entry
                    tp_target = 0.008 if self.paper_inventory < 5 else 0.004
                    
                    if profit >= tp_target or (z_score > 2.0 and profit > 0.0002):
                        profit_usd = invested_amount * profit
                        self.paper_balance += invested_amount + profit_usd
                        print(f"💰 [SELL] RECORDED @ {price:.3f} (+{profit*100:.2f}%)")
                        self.log_trade("SELL", price, z_score, invested_amount, profit_usd, total_equity)
                        self.paper_inventory = 0
                        self.avg_entry = 0

                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🏁 Musta laatikko suljettu.")

if __name__ == "__main__":
    FerrariV22().run()
