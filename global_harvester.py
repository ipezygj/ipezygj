import asyncio
import time
import csv
import os
from hl_ghost import HyperGhost
from derivative import UniversalScanner

async def global_harvest():
    ghost = HyperGhost()
    scanner = UniversalScanner()
    log_file = "global_market_log.csv"
    
    # Kassa ja asetukset
    ghost_balance = 101.0  # Jatketaan siitä mihin jäätiin
    trade_size = 100.0
    history = [] # Tähän tallentuu lyhyt muisti (opiskelu)
    
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["ts", "m_price", "b_price", "hl_price", "gap", "trend", "profit"])

    print(f"\n🧠 FERRARI NEURAL HARVESTER | Learning Mode Active")
    print("-" * 80)
    
    try:
        while True:
            results = await scanner.scan_all("ETH")
            m_price = next((r['price'] for r in results if r['exchange'] == 'MEXC_SPOT'), None)
            b_price = next((r['price'] for r in results if r['exchange'] == 'BINANCE_SPOT'), None)
            hl_price = ghost.get_price("ETH")
            
            if all([m_price, b_price, hl_price]):
                prices = [m_price, b_price, hl_price]
                max_gap = (max(prices) - min(prices)) / min(prices) * 100
                ts = time.strftime('%H:%M:%S')
                
                # --- OPISKELU-OSIO (Rolling Memory) ---
                history.append(max_gap)
                if len(history) > 10: history.pop(0) # Pidetään vain viimeiset 10 sekuntia
                
                # Lasketaan trendi: onko gap kasvamassa vai pienenemässä?
                trend = "STABLE"
                if len(history) >= 2:
                    if history[-1] > history[-2]: trend = "EXPANDING"
                    elif history[-1] < history[-2]: trend = "SHRINKING"
                
                # --- ADAPTIIVINEN ISKU ---
                profit_step = 0
                status = "⚖️"
                
                # Opiskeltu ehto: Isketään vain jos gap on iso JA se on laajenemassa (momentum)
                if max_gap >= 0.08 and trend == "EXPANDING":
                    profit_step = trade_size * ((max_gap - 0.02) / 100)
                    ghost_balance += profit_step
                    status = "💰 NEURAL HIT!"
                
                # Tallennus
                with open(log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([ts, m_price, b_price, hl_price, f"{max_gap:.4f}", trend, f"{profit_step:.4f}"])
                
                print(f"[{ts}] Gap: {max_gap:.4f}% | Trend: {trend.ljust(9)} | Wallet: {ghost_balance:.4f}€ {status}")

            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\nFinal Wallet: {ghost_balance:.2f}€")
    finally:
        await scanner.close()

if __name__ == "__main__":
    asyncio.run(global_harvest())
