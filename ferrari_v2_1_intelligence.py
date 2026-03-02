""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import statistics

class FerrariV21:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
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

        self.preload_history()
        print(f"🧪 FERRARI V2.1 INTELLIGENCE. Kassa: ${self.paper_balance:.2f}")

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
        print(f"\n🏎️  FERRARI V2.1 - INTELLIGENCE PACK ACTIVE")
        print("-" * 85)
        
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
                
                # DYNAAMINEN JÄÄHDYTYS JA TILA
                current_cooldown = self.base_cooldown
                if volatility_ratio < 0.0005: 
                    mode = "SNIPER"
                elif volatility_ratio > 0.0025:
                    mode = "SHIELD"
                    current_cooldown = self.base_cooldown * 2 # 90s jäähy paniikissa
                else:
                    mode = "CRUISE"

                time_since_last = time.time() - self.last_buy_time
                cooldown_active = time_since_last < current_cooldown
                
                status = "READY"
                if cooldown_active: status = f"❄️ COOL ({int(current_cooldown - time_since_last)}s)"
                if self.paper_inventory >= self.max_inventory: status = "⛔ MAX LOAD"

                invested_amount = self.paper_inventory * self.trade_size
                risk_pct = (invested_amount / (self.paper_balance + invested_amount)) * 100
                
                pnl_str = "FLAT"
                if self.paper_inventory > 0:
                    profit_pct = (price - self.avg_entry) / self.avg_entry
                    color = "🟢" if profit_pct > 0 else "🔴"
                    pnl_str = f"{color} {profit_pct*100:.2f}%"

                total_equity = self.paper_balance + invested_amount + (invested_amount * (profit_pct if self.paper_inventory > 0 else 0))
                
                print(f"HYPE: {price:.3f} | 💰 ${total_equity:.2f} | ☢️ RISK: {risk_pct:.0f}% | {mode} | {status} | {pnl_str}")

                # OSTO
                if z_score <= self.base_trigger and self.paper_inventory < self.max_inventory:
                    if not cooldown_active:
                        print(f"🚀 [BUY] OSTA @ {price:.3f} (Z: {z_score:.2f})")
                        self.paper_balance -= self.trade_size
                        self.paper_inventory += 1
                        if self.avg_entry == 0: self.avg_entry = price
                        else: self.avg_entry = ((self.avg_entry * (self.paper_inventory-1)) + price) / self.paper_inventory
                        self.last_buy_time = time.time()

                # MYYNTI
                elif self.paper_inventory > 0:
                    profit = (price - self.avg_entry) / self.avg_entry
                    # Kevennetään lastia jos ollaan raskaassa lastissa
                    tp_target = 0.008 if self.paper_inventory < 5 else 0.004
                    
                    if profit >= tp_target or (z_score > 2.0 and profit > 0.0002):
                        profit_usd = invested_amount * profit
                        self.paper_balance += invested_amount + profit_usd
                        print(f"💰 [SELL] MYY @ {price:.3f} (+{profit*100:.2f}%) | Voitto: ${profit_usd:.2f}")
                        self.paper_inventory = 0
                        self.avg_entry = 0

                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🏁 Simulaatio ohi.")

if __name__ == "__main__":
    FerrariV21().run()
