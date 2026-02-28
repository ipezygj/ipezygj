""" Technical implementation for Hummingbot Gateway V2.1. """

import asyncio
import logging
import random
import time
from .derivative import UniversalScanner

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    scanner = UniversalScanner()
    logger.info("🧙‍♂️ Gandalf Sauce Activated: Volatility-based Stealth enabled.")

    last_price = None
    
    try:
        while True:
            results = await scanner.scan_all("ETH")
            valid = [r for r in results if r.get('status') == 200 and 'price' in r]
            
            if valid:
                current_price = valid[0]['price']
                
                # Lasketaan "markkinan hermostuneisuus"
                volatility = abs(current_price - last_price) if last_price else 0
                last_price = current_price
                
                # Dynaaminen viive: jos volatiteetti kasvaa, botti nopeutuu
                # Mutta pidetään aina vähintään 5s väli (Safety First)
                base_wait = 45 if volatility < 0.5 else 10
                wait_time = random.uniform(base_wait * 0.8, base_wait * 1.2)
                
                logger.info(f"📈 Price: {current_price} | Vol: {volatility:.2f} | Next scan in {wait_time:.1f}s")
            
            await asyncio.sleep(wait_time)
            
    except Exception as e:
        logger.error(f"❌ Critical: {e}")
    finally:
        await scanner.close()

if __name__ == "__main__":
    asyncio.run(main())
