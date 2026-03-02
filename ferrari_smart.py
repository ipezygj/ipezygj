""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import json
import os
import datetime

class FerrariSmart:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.log_file = "ferrari_ledger.md"
        
        # 🧠 ÄLYKÄS MUISTI (Tarkka)
        self.memory_length = 20    # Pidetään se herkkänä (20)
        self.price_memory = []
        
        # ⚡ KALIBROITU TRIGGERI (Fiksu)
        self.base_trigger = -1.0   # KULTAINEN KESKITIE (Ei liian tiukka, ei liian löysä)
        
        # 💰 RAHANHALLINTA
        self.max_roll = 10.0
        self.trade_size = 3.0
        self.inventory = 0
        self.avg_entry = 0.0

        self.preload_history()
        self.log_event("SYSTEM_START", "Ferrari Smart Engine (Calibrated) käynnistetty.")

    def log_event(self, event_type, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"| {timestamp} | {event_type} | {message} |\n")

    def preload_history(self):
        print("📥 Kalibroidaan 'Hot Data' pörssistä...", end="")
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

    def get_price(self):
        try:
            r = requests.post(self.info_url, json={"type": "allMids"}).json()
            return float(r.get('HYPE', 0))
        except: return 0

    def calculate_smart_logic(self, current_price):
        self.price_memory.append(current_price)
        if len(self.price_memory) > self.memory_length: self.price_memory.pop(0)

        if len(self.price_memory) < 5: return 0, 0, "INIT"

        mean = statistics.mean(self.price_memory)
        stdev = statistics.stdev(self.price_memory)
        
        if stdev == 0: return 0, 0, "FLAT"

        z_score = (current_price - mean) / stdev
        volatility_ratio = stdev / mean
        
        # 🔥 ÄLYKÄS MODULOINTI 🔥
        # Korjattu aiempi virhe: Nostettu rajoja, jotta "SHIELD" ei mene päälle turhaan.
        
        # 1. SNIPER (Rauhallinen markkina): Hinta vain lilluu -> Ole tarkka, nappaa pienet
        if volatility_ratio < 0.0005: 
            sensitivity = 0.8  # Trig -> -0.80 (Ostaa pienet dipit)
            mode = "SNIPER (Calm)"
            
        # 2. SHIELD (Aito paniikki): Vasta kun vola on oikeasti isoa -> Mene suojaan
        elif volatility_ratio > 0.0025: # Nostettu raja (oli 0.0010)
            sensitivity = 1.5  # Trig -> -1.50 (Ostaa vain romahdukset)
            mode = "SHIELD (Panic)"
            
        # 3. CRUISE (Normaali): Perusasetus
        else:
            sensitivity = 1.0  # Trig -> -1.00 (Standard Deviation liike)
            mode = "CRUISE (Normal)"

        dynamic_trigger = self.base_trigger * sensitivity
        
        return z_score, dynamic_trigger, mode

    def run(self):
        print(f"\n🧠 FERRARI SMART - INTELLIGENT TRADING")
        print(f"⚖️  Base Trigger: {self.base_trigger} | Calibrated Limits")
        print("-" * 65)
        
        try:
            while True:
                price = self.get_price()
                if price == 0: continue
                
                z_score, dyn_trig, mode = self.calculate_smart_logic(price)
                
                # Mittaristo
                print(f"HYPE: {price:.3f} | Z: {z_score:.2f} | Trig: {dyn_trig:.2f} | {mode}")

                # --- KAUPANKÄYNTI ---
                
                # OSTO: Fiksu liike
                if z_score <= dyn_trig and (self.inventory * self.trade_size) < self.max_roll:
                    print(f"🚀 SMART ENTRY! ({mode}) - Z: {z_score:.2f}")
                    self.inventory += 1
                    self.avg_entry = price
                    self.log_event("SMART_BUY", f"Price: {price}, Z: {z_score}, Mode: {mode}")

                # MYYNTI: Voitto kotiin
                elif self.inventory > 0:
                    profit = (price - self.avg_entry) / self.avg_entry
                    
                    # Myydään jos voitto on hyvä TAI hinta on "ylilyönti" ylöspäin (Z > 1.2)
                    if profit >= 0.008 or z_score > 1.2:
                        print(f"💰 PROFIT SECURED! (+{profit*100:.2f}%)")
                        self.inventory = 0
                        self.log_event("SMART_SELL", f"Profit: {profit*100:.2f}%")

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🏁 Ferrari pysäytetty hallitusti.")

if __name__ == "__main__":
    FerrariSmart().run()
