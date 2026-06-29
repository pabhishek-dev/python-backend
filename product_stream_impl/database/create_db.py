import sqlite3

conn = sqlite3.connect("track_info.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
               name TEXT,
               price REAL,
               stock INTEGER,
               imageUrl TEXT,
               desc TEXT,
               category TEXT,
               rating REAL
               )
    """)

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
conn.commit()

