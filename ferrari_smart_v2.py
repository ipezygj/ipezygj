""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import datetime

class FerrariSmartV2:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        self.log_file = "ferrari_ledger.md"
        
        # 🧠 ASETUKSET
        self.memory_length = 20
        self.price_memory = []
        self.base_trigger = -1.0
        
        # 💰 RAHANHALLINTA
        self.max_roll = 10.0
        self.trade_size = 3.0
        self.inventory = 0
        self.avg_entry = 0.0
        
        # ❄️ JÄÄHDYTYS (ESTÄÄ KONEKIVÄÄRIN)
        self.last_buy_time = 0
        self.cooldown_seconds = 45 

        self.preload_history()
        self.log_event("SYSTEM_START", "Ferrari Smart V2 (Cooldown & Profit Guard) käynnistetty.")

    def log_event(self, event_type, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"| {timestamp} | {event_type} | {message} |\n")

    def preload_history(self):
        print("📥 Ladataan dataa...", end="")
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

    def run(self):
        print(f"\n🧠 FERRARI SMART V2 - THE PROFESSIONAL")
        print(f"❄️  Cooldown: {self.cooldown_seconds}s | 🛡️ Profit Guard Active")
        print("-" * 65)
        
        try:
            while True:
                price = self.get_price()
                if price == 0: continue
                
                self.price_memory.append(price)
                if len(self.price_memory) > self.memory_length: self.price_memory.pop(0)
                
                if len(self.price_memory) < 5: continue

                mean = statistics.mean(self.price_memory)
                stdev = statistics.stdev(self.price_memory)
                
                if stdev == 0: continue

                z_score = (price - mean) / stdev
                volatility_ratio = stdev / mean
                
                # Dynaaminen tila
                if volatility_ratio < 0.0005: 
                    dyn_trig = self.base_trigger * 0.8
                    mode = "SNIPER"
                elif volatility_ratio > 0.0025:
                    dyn_trig = self.base_trigger * 1.5
                    mode = "SHIELD"
                else:
                    dyn_trig = self.base_trigger
                    mode = "CRUISE"

                # Laske aika viime kaupasta
                time_since_last = time.time() - self.last_buy_time
                cooldown_active = time_since_last < self.cooldown_seconds

                # Mittaristo: Näytä myös aika jäähtymisen päättymiseen
                status_msg = f"READY"
                if cooldown_active:
                    status_msg = f"❄️ COOLING ({int(self.cooldown_seconds - time_since_last)}s)"
                
                print(f"HYPE: {price:.3f} | Z: {z_score:.2f} | {mode} | {status_msg}")

                # --- OSTO ---
                if z_score <= dyn_trig and (self.inventory * self.trade_size) < self.max_roll:
                    if not cooldown_active:
                        print(f"🚀 SMART ENTRY! (Z: {z_score:.2f})")
                        self.inventory += 1
                        # Lasketaan uusi keskihinta (Painotettu keskiarvo)
                        if self.avg_entry == 0: self.avg_entry = price
                        else: self.avg_entry = ((self.avg_entry * (self.inventory-1)) + price) / self.inventory
                        
                        self.last_buy_time = time.time() # Käynnistä kello
                        self.log_event("BUY", f"Price: {price:.3f}, Z: {z_score:.2f}")
                    else:
                        # Hiljainen hylkäys jäähdyttelyn takia (ei spammata logia)
                        pass

                # --- MYYNTI (KORJATTU LOGIIKKA) ---
                elif self.inventory > 0:
                    profit = (price - self.avg_entry) / self.avg_entry
                    
                    # EHTO 1: Kunnon voitto (0.8%)
                    take_profit = profit >= 0.008
                    
                    # EHTO 2: Tekninen piikki (Z > 2.0) MUTTA vain jos ollaan voitolla kulujen jälkeen
                    technical_exit = (z_score > 2.0 and profit > 0.001) 
                    
                    if take_profit or technical_exit:
                        reason = "TARGET" if take_profit else "SPIKE"
                        print(f"💰 PROFIT SECURED ({reason})! (+{profit*100:.2f}%)")
                        self.inventory = 0
                        self.avg_entry = 0
                        self.log_event("SELL", f"Profit: {profit*100:.2f}% ({reason})")

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n🏁 Ferrari pysäytetty.")

if __name__ == "__main__":
    FerrariSmartV2().run()
