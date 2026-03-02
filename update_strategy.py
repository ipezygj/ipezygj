import os

path = os.path.expanduser('~/my_ferrari/strategy.py')
with open(path, 'r') as f:
    code = f.read()

# Lisätään importit
if 'import sqlite3' not in code:
    code = "import sqlite3\n" + code

# Lisätään tallennuslogiikka print-lauseen perään
old_line = 'print(f"🔮 Pyth ETH/USD: ${price}")'
new_line = old_line + """
            try:
                conn = sqlite3.connect(os.path.expanduser('~/my_ferrari/strategy.db'))
                c = conn.cursor()
                c.execute("INSERT INTO prices (pair, price) VALUES (?, ?)", ('ETH/USD', price))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"❌ DB Error: {e}")"""

if old_line in code and "INSERT INTO prices" not in code:
    code = code.replace(old_line, new_line)
    with open(path, 'w') as f:
        f.write(code)
    print("✅ strategy.py updated with SQLite persistence.")
else:
    print("⚠️ Update skipped: already updated or pattern not found.")
