""" Technical implementation for Hummingbot Gateway V2.1. """
import requests
import time
import math
import statistics

class NeuralFerrari:
    def __init__(self):
        self.info_url = "https://api.hyperliquid.xyz/info"
        
        # 🧠 NEURAL SETTINGS (Aivot)
        self.memory_length = 20    # Kuinka monta hintapistettä muistetaan
        self.price_memory = []     # Lyhytkestoinen muisti
        self.z_score_trigger = -2.0 # "Panic sell" -taso, josta me ostamme (2x keskihajonta)
        self.take_profit_pct = 0.008 # 0.8% voitto riittää (Scalping)
        
        # 💰 RISK MANAGEMENT (Lompakko)
        self.trade_size_usd = 3.0  # Minimi, jotta menee läpi ($3)
        self.max_inventory = 3     # Max 3 positiota kerralla auki ($9 riski)
        self.current_inventory = 0
        self.avg_entry_price = 0.0

    def get_price(self):
        try:
            r = requests.post(self.info_url, json={"type": "allMids"}, timeout=2).json()
            return float(r.get('HYPE', 0))
        except: return 0

    def calculate_neuro_metrics(self):
        if len(self.price_memory) < self.memory_length:
            return None, None
        
        # Lasketaan liukuva keskiarvo ja volatiliteetti
        mean = statistics.mean(self.price_memory)
        stdev = statistics.stdev(self.price_memory)
        return mean, stdev

    def execute_logic(self, current_price):
        # Lisää hinta muistiin
        self.price_memory.append(current_price)
        if len(self.price_memory) > self.memory_length:
            self.price_memory.pop(0) # Unohda vanhin

        mean, stdev = self.calculate_neuro_metrics()
        
        if mean is None:
            print(f"⏳ NEURAL LOADING... ({len(self.price_memory)}/{self.memory_length})")
            return

        # 🧠 Z-Score kertoo kuinka "kaukana" normaalista ollaan
        if stdev == 0: return
        z_score = (current_price - mean) / stdev
        
        # Tulostetaan "aivojen" tila
        signal_strength = "🟢 NEUTRAL"
        if z_score < -1.5: signal_strength = "🟡 OVERSOLD (Watching)"
        if z_score < self.z_score_trigger: signal_strength = "🔴 SUPER DIP (BUY ZONE)"
        if z_score > 1.5: signal_strength = "🔵 OVERBOUGHT"

        print(f"🧠 Price: ${current_price:.3f} | Mean: ${mean:.3f} | Z-Score: {z_score:.2f} | {signal_strength}")

        # --- KAUPANKÄYNTILOGIIKKA ---
        
        # 1. OSTO-SIGNAALI (Kun kaikki muut myyvät paniikissa)
        if z_score <= self.z_score_trigger and self.current_inventory < self.max_inventory:
            print(f"🚀 NEURAL TRIGGER: BUY SIGNAL @ ${current_price:.3f}")
            # Tähän tulisi self.vault.execute_trade(...)
            # Simulaatio oston onnistumisesta:
            self.avg_entry_price = ((self.avg_entry_price * self.current_inventory) + current_price) / (self.current_inventory + 1)
            self.current_inventory += 1
            print(f"✅ POSITION ADDED. Inventory: {self.current_inventory} | Avg Price: ${self.avg_entry_price:.3f}")

        # 2. MYYNTI-SIGNAALI (Kun tavoite on saavutettu)
        elif self.current_inventory > 0:
            profit_pct = (current_price - self.avg_entry_price) / self.avg_entry_price
            if profit_pct >= self.take_profit_pct:
                print(f"💰 NEURAL PROFIT: SELL SIGNAL @ ${current_price:.3f} (Profit: {profit_pct*100:.2f}%)")
                self.current_inventory = 0
                self.avg_entry_price = 0

    def run(self):
        print(f"\n🧠 NEURAL FERRARI ACTIVE - LEARNING MODE")
        print(f"📉 Trigger: Z-Score {self.z_score_trigger} (Statistical Bottom)")
        print("-" * 60)
        
        try:
            while True:
                price = self.get_price()
                if price > 0:
                    self.execute_logic(price)
                time.sleep(3) # Nopea sykli
        except KeyboardInterrupt:
            print("\n🏁 Neural Ferrari pysäytetty.")

if __name__ == "__main__":
    NeuralFerrari().run()
