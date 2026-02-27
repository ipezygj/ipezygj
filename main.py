""" Technical implementation for Ferrari Stealth Syndicate V3.5 - Deep Space Stealth. """
import asyncio

from cosmic_foundry import fetch_cosmic_data
from deep_space_radar import run_deep_space_radar
from strategy import run_alpha_strategy


async def run_cosmic_loop():
    try:
        while True:
            await fetch_cosmic_data()
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"❌ [COSMIC] Error: {e}")

async def safe_alpha_strategy():
    try:
        await run_alpha_strategy()
    except Exception as e:
        print(f"🔥 [CRITICAL] Alpha Engine kaatui: {e}")

async def main():
    print("💎 FERRARI STEALTH SYNDICATE V3.5: DEEP SPACE STEALTH EDITION")
    print("🏎️  Paja käynnistyy: Alpha, Cosmic News & <100m NEO Mapper active...")
    
    await asyncio.gather(
        safe_alpha_strategy(),
        run_cosmic_loop(),
        run_deep_space_radar() # ☄️ AITO NASA JPL <100m TELEMETRIA KYTKETTY!
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🏁 Pit Stop: Ferrari safely in the garage.")
