import sqlite3

conn = sqlite3.connect('urlshortener.db')
cursor = conn.cursor()

# Ver tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("📋 Tablas en SQLite:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()
