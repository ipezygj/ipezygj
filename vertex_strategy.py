""" Technical implementation for Vertex Protocol V6 - Bounty Edition. """

import asyncio
import collections
import sqlite3
from datetime import datetime

import httpx

DB_FILE = "stealth_state.db"

class StateManager:
    def __init__(self):
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS wallet (balance REAL)''')
            c.execute('''CREATE TABLE IF NOT EXISTS inventory 
                         (asset TEXT PRIMARY KEY, amount REAL, buy_price REAL, max_seen_price REAL)''')
            c.execute('SELECT balance FROM wallet')
            if not c.fetchone():
                c.execute('INSERT INTO wallet VALUES (1000.0)')
            conn.commit()

    def load_state(self, targets):
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('SELECT balance FROM wallet')
            balance = c.fetchone()[0]
            inventory = {asset: 0.0 for asset in targets}
            buy_prices = {asset: 0.0 for asset in targets}
            max_seen = {asset: 0.0 for asset in targets}
            c.execute('SELECT asset, amount, buy_price, max_seen_price FROM inventory')
            for row in c.fetchall():
                if row[0] in targets:
                    inventory[row[0]] = row[1]
                    buy_prices[row[0]] = row[2]
                    max_seen[row[0]] = row[3]
            return balance, inventory, buy_prices, max_seen

    def save_state(self, balance, asset, amount, buy_price, max_seen):
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('UPDATE wallet SET balance = ?', (balance,))
            c.execute('''INSERT OR REPLACE INTO inventory (asset, amount, buy_price, max_seen_price) 
                         VALUES (?, ?, ?, ?)''', (asset, amount, buy_price, max_seen))
            conn.commit()

class TelegramReporter:
    def __init__(self, token, channels):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.channels = channels

    async def route_signal(self, target_channel, message):
        chat_id = self.channels.get(target_channel)
        if not chat_id: return
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            async with httpx.AsyncClient() as client:
                await client.post(self.url, json=payload, timeout=5.0)
        except Exception: pass

class VertexStealthRadar:
    def __init__(self, tg_token, tg_channels):
        self.api_url = "https://gateway.prod.vertexprotocol.com/api/v6/symbols"
        self.targets = ["BTC-PERP", "ETH-PERP", "ARB-PERP", "SOL-PERP", "TIA-PERP"]
        self.max_trade_pct = 0.10
        self.lock = asyncio.Lock()
        self.history = {asset: collections.deque(maxlen=15) for asset in self.targets}
        self.tg = TelegramReporter(tg_token, tg_channels)
        self.db = StateManager()
        self.balance, self.inventory, self.buy_prices, self.max_seen_price = self.db.load_state(self.targets)

    async def run(self):
        print(f"🏎️  VERTEX BOUNTY RADAR STARTING")
        await self.tg.route_signal("SIGNAL", f"🟢 *Vertex Bounty Radar*\nSystem Check: OK. Monitoring Arbitrum markets.")

        async with httpx.AsyncClient() as client:
            while True:
                try:
                    resp = await client.get(self.api_url, timeout=5.0)
                    data = resp.json()
                    # Vertex palauttaa listan symboleista
                    mids = {item['symbol']: float(item['price']) for item in data if 'symbol' in item}
                except Exception as e:
                    await asyncio.sleep(1)
                    continue

                for asset in self.targets:
                    if asset not in mids: continue
                    price = mids[asset]
                    self.history[asset].append(price)
                    if len(self.history[asset]) < 10: continue

                    avg = sum(self.history[asset]) / len(self.history[asset])
                    
                    async with self.lock:
                        if self.inventory[asset] == 0 and price < (avg * 0.9992):
                            val = self.balance * self.max_trade_pct
                            self.inventory[asset] = val / price
                            self.balance -= val
                            self.buy_prices[asset] = price
                            self.max_seen_price[asset] = price
                            self.db.save_state(self.balance, asset, self.inventory[asset], price, price)
                            msg = f"✅ *VERTEX ENTRY: {asset}*\nPrice: {price}\nCash: {round(self.balance, 2)} USDC"
                            asyncio.create_task(self.tg.route_signal("SIGNAL", msg))

                        elif self.inventory[asset] > 0:
                            if price > self.max_seen_price[asset]:
                                self.max_seen_price[asset] = price
                                self.db.save_state(self.balance, asset, self.inventory[asset], self.buy_prices[asset], price)
                            
                            p_pct = (price - self.buy_prices[asset]) / self.buy_prices[asset]
                            if p_pct > 0.002 and price < (self.max_seen_price[asset] * 0.9995) or p_pct < -0.008:
                                final_val = price * self.inventory[asset]
                                self.balance += final_val
                                self.inventory[asset] = 0.0
                                self.db.save_state(self.balance, asset, 0.0, 0.0, 0.0)
                                msg = f"🛑 *VERTEX EXIT: {asset}*\nPrice: {price}\nBalance: {round(self.balance, 2)}"
                                asyncio.create_task(self.tg.route_signal("SIGNAL", msg))

                await asyncio.sleep(0.5)

if __name__ == "__main__":
    TOKEN = "8747958578:AAEKbU1p0jCPt61R8Nnd3YOIjKyw8z3ana4"
    CHANNELS = {"SIGNAL": "-1003737212742"}
    asyncio.run(VertexStealthRadar(TOKEN, CHANNELS).run())
