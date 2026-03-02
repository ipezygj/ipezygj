""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import datetime

class FerrariSimulator:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        
        # 🧪 SIMULAATTORIN ASETUKSET
        self.paper_balance = 100.00  # Aloitetaan sadalla dollarilla (virtuaali)
        self.paper_inventory = 0     # Montako "siivua" omistamme
        self.avg_entry = 0.0         # Keskiostohinta
        
        # 🧠 ÄLYKÄS LOGIIKKA
        self.memory_length = 20
        self.price_memory = []
        self.base_trigger = -1.0
        
        # 💰 RAHANHALLINTA
        self.trade_size = 3.0        # Yksi siivu on $3
        self.max_inventory = 3       # Max 3 siivua kerralla ($9 riski)
        
        # ❄️ JÄÄHDYTYS (Cooldown)
        self.last_buy_time = 0
        self.cooldown_seconds = 45   # 45s pakollinen tauko ostojen välillä

        self.preload_history()
        print(f"🧪 SIMULAATTORI KÄYNNISTETTY. Kassa: ${self.paper_balance:.2f}")

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

    def get_price(self):
        try:
            r = requests.post(self.info_url, json={"type": "allMids"}).json()
            return float(r.get('HYPE', 0))
        except: return 0

    def run(self):
        print(f"\n🏎️  FERRARI WIND TUNNEL (PAPER MODE)")
        print(f"❄️  Cooldown: {self.cooldown_seconds}s | 🛡️ Profit Guard Active")
        print("-" * 75)
        
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
                
                # --- DYNAAMINEN TILA ---
                if volatility_ratio < 0.0005: 
                    dyn_trig = self.base_trigger * 0.8
                    mode = "SNIPER"
                elif volatility_ratio > 0.0025:
                    dyn_trig = self.base_trigger * 1.5
                    mode = "SHIELD"
                else:
                    dyn_trig = self.base_trigger
                    mode = "CRUISE"

                # Jäähdytyslaskuri
                time_since_last = time.time() - self.last_buy_time
                cooldown_active = time_since_last < self.cooldown_seconds
                
                # Tilannekatsaus (Mitä tekee?)
                status = "READY"
                if cooldown_active: status = f"❄️ COOL ({int(self.cooldown_seconds - time_since_last)}s)"
                if self.paper_inventory >= self.max_inventory: status = "MAX LOAD"

                # Voittolaskelma (Jos positiossa)
                pnl_str = "FLAT"
                current_profit_usd = 0.0
                if self.paper_inventory > 0:
                    profit_pct = (price - self.avg_entry) / self.avg_entry
                    current_profit_usd = (self.paper_inventory * self.trade_size) * profit_pct
                    color = "🟢" if profit_pct > 0 else "🔴"
                    pnl_str = f"{color} {profit_pct*100:.2f}% (${current_profit_usd:.2f})"

                # 📊 MITTARISTO (Tämä on se mitä pyysit)
                total_equity = self.paper_balance + (self.paper_inventory * self.trade_size) + current_profit_usd
                print(f"HYPE: {price:.3f} | 💰 ${total_equity:.2f} | Z: {z_score:.2f} | {mode} | {status} | {pnl_str}")

                # --- OSTO-SIMULAATIO ---
                if z_score <= dyn_trig and self.paper_inventory < self.max_inventory:
                    if not cooldown_active:
                        print(f"🚀 [SIMULATED BUY] OSTA @ {price:.3f} (Z: {z_score:.2f})")
                        self.paper_balance -= self.trade_size
                        self.paper_inventory += 1
                        # Keskihinnan päivitys
                        if self.avg_entry == 0: self.avg_entry = price
                        else: self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + price) / self.paper_inventory
                        
                        self.last_buy_time = time.time()
                    else:
                        pass # Jäähdytys estää tulituksen

                # --- MYYNTI-SIMULAATIO ---
                elif self.paper_inventory > 0:
                    profit = (price - self.avg_entry) / self.avg_entry
                    
                    # Myyntisäännöt: Voitto > 0.8% TAI (Z > 2.0 JA Voitto > 0.02% kulujen jälkeen)
                    take_profit = profit >= 0.008
                    technical_exit = (z_score > 2.0 and profit > 0.0002)
                    
                    if take_profit or technical_exit:
                        reason = "TARGET" if take_profit else "SPIKE"
                        profit_usd = (self.paper_inventory * self.trade_size) * profit
                        self.paper_balance += (self.paper_inventory * self.trade_size) + profit_usd
                        
                        print(f"💰 [SIMULATED SELL] MYY @ {price:.3f} (+{profit*100:.2f}%) | Voitto: ${profit_usd:.2f}")
                        
                        self.paper_inventory = 0
                        self.avg_entry = 0

                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n🏁 Simulaatio ohi. Loppusaldosi: ${total_equity:.2f}")

if __name__ == "__main__":
    FerrariSimulator().run()
