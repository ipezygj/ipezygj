""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics
import datetime

class FerrariSimulatorV2:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        
        # 🧪 SIMULAATTORIN ASETUKSET
        self.paper_balance = 100.00
        self.paper_inventory = 0
        self.avg_entry = 0.0
        
        # 🧠 ÄLYKÄS LOGIIKKA
        self.memory_length = 20
        self.price_memory = []
        self.base_trigger = -1.0
        
        # 💰 FERRARI SCALING (RISKIHALLINTA)
        self.trade_size = 3.0
        self.max_inventory = 10      # NYT: 10 siivua (Max riski $30 eli 30%)
        
        # ❄️ JÄÄHDYTYS
        self.last_buy_time = 0
        self.cooldown_seconds = 45

        self.preload_history()
        print(f"🧪 SIMULAATTORI V2 (V12 ENGINE). Kassa: ${self.paper_balance:.2f}")

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
        print(f"\n🏎️  FERRARI SIMULATOR V2 - HEAVY LOAD EDITION")
        print(f"🔫  Magazine: {self.max_inventory} rounds | ❄️ Cooldown: {self.cooldown_seconds}s")
        print("-" * 80)
        
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

                time_since_last = time.time() - self.last_buy_time
                cooldown_active = time_since_last < self.cooldown_seconds
                
                # Status
                status = "READY"
                if cooldown_active: status = f"❄️ COOL ({int(self.cooldown_seconds - time_since_last)}s)"
                if self.paper_inventory >= self.max_inventory: status = "⛔ MAX LOAD"

                # Profit & Risk
                pnl_str = "FLAT"
                current_profit_usd = 0.0
                invested_amount = self.paper_inventory * self.trade_size
                risk_pct = (invested_amount / (self.paper_balance + invested_amount)) * 100
                
                if self.paper_inventory > 0:
                    profit_pct = (price - self.avg_entry) / self.avg_entry
                    current_profit_usd = invested_amount * profit_pct
                    color = "🟢" if profit_pct > 0 else "🔴"
                    pnl_str = f"{color} {profit_pct*100:.2f}% (${current_profit_usd:.2f})"

                total_equity = self.paper_balance + invested_amount + current_profit_usd
                
                # 📊 UUSI NÄYTTÖ: Sisältää RISK-mittarin
                print(f"HYPE: {price:.3f} | 💰 ${total_equity:.2f} | ☢️ RISK: {risk_pct:.0f}% ({self.paper_inventory}/{self.max_inventory}) | {status} | {pnl_str}")

                # --- OSTO ---
                if z_score <= dyn_trig and self.paper_inventory < self.max_inventory:
                    if not cooldown_active:
                        print(f"🚀 [BUY] OSTA @ {price:.3f} (Z: {z_score:.2f})")
                        self.paper_balance -= self.trade_size
                        self.paper_inventory += 1
                        if self.avg_entry == 0: self.avg_entry = price
                        else: self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + price) / self.paper_inventory
                        self.last_buy_time = time.time()
                    else:
                        pass 

                # --- MYYNTI ---
                elif self.paper_inventory > 0:
                    profit = (price - self.avg_entry) / self.avg_entry
                    take_profit = profit >= 0.008
                    technical_exit = (z_score > 2.0 and profit > 0.0002)
                    
                    if take_profit or technical_exit:
                        profit_usd = invested_amount * profit
                        self.paper_balance += invested_amount + profit_usd
                        print(f"💰 [SELL] MYY @ {price:.3f} (+{profit*100:.2f}%) | Voitto: ${profit_usd:.2f}")
                        self.paper_inventory = 0
                        self.avg_entry = 0

                time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n🏁 V2 Simulaatio ohi.")

if __name__ == "__main__":
    FerrariSimulatorV2().run()
