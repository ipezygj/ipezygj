""" Technical implementation for Signal Foundry V3.0 - Direct Radio Path. """
import asyncio
from telegram_bot import send_alpha_alert

class SignalFoundry:
    def __init__(self, initial_capital=200.0):
        self.capital = initial_capital
        self.total_profit = 0.0
        print("🔧 [FOUNDRY] Factory initialized and ready.")

    async def broadcast_signal(self, signal):
        """ Vastaanottaa signaalin ja puskee sen välittömästi radiolle. """
        entry_price = float(signal.get('price', 0))
        custom_info = signal.get("custom_msg", "")
        
        print(f"📡 [FOUNDRY] Processing signal: {custom_info[:30]}...")

        if custom_info:
            # TÄMÄ ON SE MEIDÄN IMBALANCE-VIESTI
            msg = f"🛰️ *STEALTH SENSOR ALERT*\n\n{custom_info}\n📍 Price: {entry_price:.2f}"
            success = await send_alpha_alert(msg)
            if success:
                print("✅ [FOUNDRY] Telegram delivery successful.")
            else:
                print("❌ [FOUNDRY] Telegram delivery FAILED. Check TOKEN/CHAT_ID.")
