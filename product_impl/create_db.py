import sqlite3

conn = sqlite3.connect("products.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT,
               price REAL,
               stock INTEGER,
               imageUrl TEXT,
               desc TEXT,
               rating REAL
               )
    """)

