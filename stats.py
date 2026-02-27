import sqlite3
import os

db_path = os.path.expanduser('~/my_ferrari/strategy.db')
if not os.path.exists(db_path):
    print("❌ No database found.")
    exit()

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("\n--- 🏎️ V12 MULTI-ASSET TELEMETRY REPORT ---")

c.execute("""
    SELECT pair, COUNT(*), MIN(price), MAX(price), AVG(price) 
    FROM prices 
    GROUP BY pair
    ORDER BY pair
""")

rows = c.fetchall()
if not rows:
    print("📊 No data collected yet.")
else:
    for row in rows:
        pair, count, min_p, max_p, avg_p = row
        volatility = max_p - min_p
        print(f"🔹 {pair} | Samples: {count}")
        print(f"   📈 Max: ${max_p:,.2f} | 📉 Min: ${min_p:,.2f}")
        print(f"   ⚖️ Avg: ${avg_p:,.2f} | ⚡ Vol: ${volatility:,.2f}")
        print("-" * 35)

conn.close()
