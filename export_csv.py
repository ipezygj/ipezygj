""" Technical implementation for Hummingbot Gateway V2.1. """
import sqlite3
import csv
import os

DB_FILE = os.path.expanduser('~/my_ferrari/strategy.db')
CSV_FILE = os.path.expanduser('~/my_ferrari/market_data.csv')

def export_data():
    if not os.path.exists(DB_FILE):
        print("❌ No DB found. Engine empty.")
        return
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, pair, price FROM prices ORDER BY timestamp ASC")
    rows = c.fetchall()
    
    with open(CSV_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'pair', 'price'])
        writer.writerows(rows)
        
    conn.close()
    print(f"✅ V12 Telemetry extracted: {len(rows)} rows saved to market_data.csv")

if __name__ == "__main__":
    export_data()
