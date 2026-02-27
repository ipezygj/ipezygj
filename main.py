""" Technical implementation for Ferrari Stealth Syndicate V3.3 - Bypass Mode. """
import asyncio
from strategy import run_alpha_strategy
from cosmic_foundry import fetch_cosmic_data

async def run_cosmic_loop():
    try:
        while True:
            await fetch_cosmic_data()
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"❌ [COSMIC] Error: {e}")

async def safe_alpha_strategy():
    try:
        print("🔧 [SYSTEM] Sytytysvirta kytketty Alpha-moottoriin! Käsijarru on irti!")
        await run_alpha_strategy()
    except Exception as e:
        print(f"🔥 [CRITICAL] Alpha Engine kaatui: {e}")

async def main():
    print("💎 FERRARI STEALTH SYNDICATE V3.3: BYPASS MODE")
    print("🏎️  Paja käynnistyy: API-palvelin ohitettu diagnostiikan ajaksi...")
    
    # KÄYNNISTETÄÄN VAIN ALPHA JA NASA (Ei API-serveriä!)
    await asyncio.gather(
        safe_alpha_strategy(),
        run_cosmic_loop()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🏁 Pit Stop: Ferrari safely in the garage.")
