""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import json
import os
import datetime

class FerrariAdaptive:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.log_file = "ferrari_ledger.md"
        
        # 🧠 ÄLYKÄS MUISTI
        self.memory_length = 30    # Sopiva balanssi (ei liian lyhyt, ei liian pitkä)
        self.price_memory = []
        
        # ⚡ DYNAAMISET ASETUKSET
        self.base_trigger = -1.2   # Lähtötaso (Alpha)
        self.current_sensitivity = 1.0 
        
        # 💰 RAHANHALLINTA
        self.max_roll = 10.0
        self.trade_size = 3.0
        self.inventory = 0
        self.avg_entry = 0.0

        # Alustus
        self.preload_history()
        self.log_event("SYSTEM_START", "Adaptive Neuro-Engine käynnistetty.")

    def log_event(self, event_type, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"| {timestamp} | {event_type} | {message} |\n")

    def preload_history(self):
        print("📥 Ladataan 'Hot Data' pörssistä...", end="")
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

    def calculate_neuro_logic(self, current_price):
        # 1. Lisää muistiin
        self.price_memory.append(current_price)
        if len(self.price_memory) > self.memory_length: self.price_memory.pop(0)

        # 2. Laske tilastot
        mean = statistics.mean(self.price_memory)
        stdev = statistics.stdev(self.price_memory)
        
        if stdev == 0: return 0, 0, 0

        # 3. Laske Z-Score (Perusälykkyys)
        z_score = (current_price - mean) / stdev

        # 4. 🔥 ADAPTIIVINEN KERROIN (Super-Älykkyys) 🔥
        # Jos volatiliteetti on PIENI (markkina nukkuu), tee triggeristä HERKEMPI.
        # Jos volatiliteetti on SUURI (panic), pidä trigger TIUKKANA.
        volatility_ratio = stdev / mean
        
        # Normaali vola on n. 0.0005. Jos se on alle sen, ollaan "Sniper Mode".
        if volatility_ratio < 0.0003:
            sensitivity = 0.7  # Herkkä (Ostaa helpommin)
            mode = "SNIPER (Low Vol)"
        elif volatility_ratio > 0.0010:
            sensitivity = 1.2  # Varovainen (Ostaa vaikeammin)
            mode = "SHIELD (High Vol)"
        else:
            sensitivity = 1.0  # Normaali
            mode = "CRUISE (Normal)"

        # Laske lopullinen dynaaminen trigger
        dynamic_trigger = self.base_trigger * sensitivity
        
        return z_score, dynamic_trigger, mode

    def run(self):
        print(f"\n🧠 FERRARI ADAPTIVE - THE SMART NEURON")
        print(f"📉 Base Trigger: {self.base_trigger} | Adapting to Volatility...")
        print("-" * 65)
        
        try:
            while True:
                price = self.get_price()
                if price == 0: continue
                
                z_score, dyn_trig, mode = self.calculate_neuro_logic(price)
                
                # Visuaalinen palaute (Mitä aivot ajattelevat?)
                print(f"HYPE: {price:.3f} | Z: {z_score:.2f} | Trig: {dyn_trig:.2f} | Mode: {mode}")

                # --- KAUPANKÄYNTI ---
                
                # OSTO: Jos Z alittaa dynaamisen rajan
                if z_score <= dyn_trig and (self.inventory * self.trade_size) < self.max_roll:
                    print(f"🚀 ÄLYKÄS OSTO! ({mode}) - Hinta poikkeuksellinen.")
                    self.inventory += 1
                    self.avg_entry = price
                    self.log_event("SMART_BUY", f"Price: {price}, Z: {z_score}, Mode: {mode}")

                # MYYNTI: Voitto tai palautuminen normaaliksi (Z > 1.0)
                elif self.inventory > 0:
                    profit = (price - self.avg_entry) / self.avg_entry
                    if profit >= 0.008 or z_score > 1.0:
                        print(f"💰 ÄLYKÄS MYYNTI! (Voitto: {profit*100:.2f}%)")
                        self.inventory = 0
                        self.log_event("SMART_SELL", f"Profit: {profit*100:.2f}%")

                time.sleep(1) # Nopea sykli

        except KeyboardInterrupt:
            print("\n🏁 Adaptive Neuron pysäytetty.")

if __name__ == "__main__":
    FerrariAdaptive().run()
