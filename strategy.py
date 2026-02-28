""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import logging
import random
from .derivative import UniversalScanner

# Setup logging - Stealth & Clean
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    scanner = UniversalScanner()
    logger.info("🧙‍♂️ Gandalf 'Hedge-Arbi' Mode: Online.")
    logger.info("🏎️ Tracking Basis (Spot vs Perp) & Cross-Exchange gaps...")

    try:
        while True:
            results = await scanner.scan_all("ETH")
            valid = [r for r in results if r.get('status') == 200]
            
            if len(valid) >= 2:
                # Erotellaan Spot ja Perp
                spots = [r for r in valid if r['type'] == 'SPOT']
                perps = [r for r in valid if r['type'] == 'PERP']
                
                # 1. Cross-Exchange Spot Arbi
                if len(spots) >= 2:
                    s_prices = [r['price'] for r in spots]
                    gap = (max(s_prices) - min(s_prices)) / min(s_prices) * 100
                    if gap > 0.05:
                        logger.warning(f"🚨 SPOT ARBI: {gap:.3f}% gap detected between spot exchanges!")

                # 2. Hedge-Arbi (Basis: Spot vs Perp)
                for s in spots:
                    for p in perps:
                        basis = (p['price'] - s['price']) / s['price'] * 100
                        if abs(basis) > 0.03:
                            direction = "CONTANGO (Perp > Spot)" if basis > 0 else "BACKWARDATION (Spot > Perp)"
                            logger.info(f"📊 BASIS [{s['exchange']} vs {p['exchange']}]: {basis:.3f}% | {direction}")

            # Stealth cooling with dynamic jitter
            wait_time = random.uniform(15, 30)
            await asyncio.sleep(wait_time)
            
    except Exception as e:
        logger.error(f"❌ Critical failure in Arbi-Engine: {e}")
    finally:
        await scanner.close()

if __name__ == "__main__":
    asyncio.run(main())
