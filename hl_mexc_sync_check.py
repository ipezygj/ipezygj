import asyncio
import time
import csv
import os
from hl_ghost import HyperGhost
from derivative import UniversalScanner

async def check_sync():
    ghost = HyperGhost()
    mexc_scanner = UniversalScanner()
    log_file = "market_sync_log.csv"
    
    # Luodaan otsikot jos tiedostoa ei ole
    if not os.path.exists(log_file):
        with open(log_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "mexc_price", "hl_price", "gap_pct"])

    print(f"\n🕵️ FERRARI DATA HARVESTER | Logging to {log_file}")
    print("-" * 60)
    
    try:
        while True:
            mexc_results = await mexc_scanner.scan_all("ETH")
            mexc_data = next((r for r in mexc_results if r['exchange'] == 'MEXC_SPOT'), None)
            hl_price = ghost.get_price("ETH")
            
            if mexc_data and hl_price:
                m_price = mexc_data['price']
                diff_pct = (abs(m_price - hl_price) / hl_price) * 100
                ts = time.strftime('%Y-%m-%d %H:%M:%S')
                
                # Kirjoitetaan lokiin
                with open(log_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([ts, m_price, hl_price, f"{diff_pct:.4f}"])
                
                status = "⚖️"
                if diff_pct > 0.05: status = "⚡"
                if diff_pct > 0.10: status = "🚀"
                
                print(f"[{ts}] M: {m_price:.2f} | H: {hl_price:.2f} | Gap: {diff_pct:.4f}% | {status}")

            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\nStopping harvester. Data saved to {log_file}")
    finally:
        await mexc_scanner.close()

if __name__ == "__main__":
    asyncio.run(check_sync())
