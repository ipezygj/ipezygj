import sqlite3
import os

db_path = os.path.expanduser('~/my_ferrari/strategy.db')
if not os.path.exists(db_path):
    print("❌ No database found.")
    exit()

conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*), MIN(price), MAX(price), AVG(price) FROM prices")
count, min_p, max_p, avg_p = c.fetchone()

print("--- 🏎️ FERRARI TELEMETRY REPORT ---")
print(f"📊 Samples collected: {count}")
if count > 0:
    print(f"📈 Max Price: ${max_p:.2f}")
    print(f"📉 Min Price: ${min_p:.2f}")
    print(f"⚖️ Average:   ${avg_p:.2f}")
    print(f"⚡ Volatility: ${max_p - min_p:.2f}")
print("----------------------------------")
conn.close()
