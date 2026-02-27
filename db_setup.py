import sqlite3
import os

db_path = os.path.expanduser('~/my_ferrari/strategy.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS prices 
             (timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
              pair TEXT, 
              price REAL)''')
conn.commit()
conn.close()
print(f"✅ Database initialized at {db_path}")
