import sqlite3

DB_FILE = "products.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def fetch_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock, imageUrl, desc, rating FROM products")
    rows = cursor.fetchall()
    conn.close()
    products = [
        {
            "id": r[0],
            "name": r[1],
            "price": r[2],
            "stock": r[3],
            "imageUrl": r[4],
            "desc": r[5],
            "rating": r[6]
        } for r in rows
    ]
    return products

def insert_product(product):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, stock, imageUrl, desc, rating) VALUES (?,?,?,?,?,?)",
        (product["name"], product["price"], product["stock"], product["imageUrl"], product["desc"], product["rating"])
    )
    conn.commit()
    conn.close()

def insert_products(products):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO products (name, price, stock, imageUrl, desc, rating) VALUES (?, ?, ?, ?, ?, ?)",
        [
            (p["name"], p["price"], p["stock"], p["imageUrl"], p["desc"], p["rating"])
            for p in products
        ]
    )

    conn.commit()
    conn.close()