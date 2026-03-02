""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import json
import os
import datetime

class FerrariCockpit:
    def __init__(self):
        self.addr = "0xbbad5d089675a0b72c00b6bf50567ca417a9b555"
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.brain_file = "neural_brain.json"
        self.log_file = "ferrari_ledger.md"
        
        # 🏎️ QUALIFYING MODE SETTINGS (Nopea & Herkkä)
        self.memory_length = 20    # Lyhyt muisti (herkkä)
        self.base_trigger = -1.5   # Alpha-taso
        self.loop_speed = 1.0      # 1 sekunnin sykli
        
        # 💰 MONEY MANAGEMENT
        self.max_roll = 10.0       # Max riski
        self.trade_size = 3.0      # Oston koko
        self.inventory = 0
        self.avg_entry = 0.0
        
        # Järjestelmät
        self.price_memory = []
        self.brain = self.load_brain()
        self.preload_history()
        self.log_event("SYSTEM_START", "Ferrari Cockpit - Mittaristo päivitetty.")

    def log_event(self, event_type, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"| {timestamp} | {event_type} | {message} |\n")

    def load_brain(self):
        try:
            with open(self.brain_file, 'r') as f: return json.load(f)
        except: return {"wins": 0, "losses": 0, "aggression": 1.0}

    def save_brain(self):
        with open(self.brain_file, 'w') as f: json.dump(self.brain, f)

    def preload_history(self):
        print("📥 Ladataan markkinadataa...", end="")
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
            print(" VALMIS.")
        except: print(" VIRHE.")

    def get_market_status(self):
        try:
            # 1. Hinta
            r_price = requests.post(self.info_url, json={"type": "allMids"}).json()
            price = float(r_price.get('HYPE', 0))
            
            # 2. Saldo (Haetaan harvemmin tai tässä tapauksessa joka kerta tarkkuuden vuoksi)
            # Optimointi: Oletetaan saldo vakaaksi silmukan sisällä, mutta haetaan nyt testiä varten
            r_state = requests.post(self.info_url, json={"type": "clearinghouseState", "user": self.addr}).json()
            balance = float(r_state.get('marginSummary', {}).get('accountValue', 0))
            
            return price, balance
        except: return 0, 0

    def run(self):
        print(f"\n🏎️  FERRARI COCKPIT - LIVE DASHBOARD")
        print(f"🔧 Setup: {self.memory_length} candles | {self.loop_speed}s loop | Trig: {self.base_trigger}")
        print("-" * 65)
        
        try:
            while True:
                price, balance = self.get_market_status()
                if price == 0: continue
                
                self.price_memory.append(price)
                if len(self.price_memory) > self.memory_length: self.price_memory.pop(0)
                
                mean = statistics.mean(self.price_memory)
                stdev = statistics.stdev(self.price_memory)
                
                if stdev == 0: continue
                
                z_score = (price - mean) / stdev
                current_trigger = self.base_trigger / self.brain['aggression']
                
                # --- MITTARISTO (DASHBOARD) ---
                # Näyttää: Hinta | Saldo | Seuraava kauppa | Z-Score
                print(f"HYPE: {price:.3f} | 💰 ${balance:.2f} | 🛒 Size: ${self.trade_size} | Z: {z_score:.2f} (Trig {current_trigger:.2f})")
                
                # --- LOGIIKKA ---
                if z_score <= current_trigger and (self.inventory * self.trade_size) < self.max_roll:
                    print(f"🚀 OSTO-SIGNAALI! (Z {z_score:.2f}) -> OSTA ${self.trade_size}")
                    self.inventory += 1
                    self.avg_entry = price # Yksinkertaistettu keskiarvo
                    self.log_event("BUY_SIGNAL", f"Price: {price}, Z: {z_score}")

                elif self.inventory > 0:
                    profit = (price - self.avg_entry) / self.avg_entry
                    if profit >= 0.008 or z_score > 1.5:
                        print(f"💰 MYYNTI-SIGNAALI! (+{profit*100:.2f}%)")
                        self.inventory = 0
                        self.log_event("SELL_SIGNAL", f"Profit: {profit*100:.2f}%")

                time.sleep(self.loop_speed)

        except KeyboardInterrupt:
            print("\n🏁 Varikko. Lopetetaan.")

if __name__ == "__main__":
    FerrariCockpit().run()
