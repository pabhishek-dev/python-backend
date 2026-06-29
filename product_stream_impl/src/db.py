import sqlite3

from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)

def fetch_products():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, stock, imageUrl, desc, category, rating FROM products")
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
            "category": r[6],
            "rating": r[7]
        } for r in rows
    ]
    return products

def fetch_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products Where id = ?", (product_id,))
    r = cursor.fetchone()

    conn.commit()
    conn.close()

    if r:
        product = {
                "id": r[0],
                "name": r[1],
                "price": r[2],
                "stock": r[3],
                "imageUrl": r[4],
                "desc": r[5],
                "category": r[6],
                "rating": r[7]
        }
        return product
    return None
    

def insert_product(product):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, stock, imageUrl, desc, category, rating) VALUES (?,?,?,?,?,?,?)",
        (product["name"], product["price"], product["stock"], product["imageUrl"], product["desc"], product["category"], product["rating"])
    )
    conn.commit()
    
    product["id"] = cursor.lastrowid
    return product

    conn.close()

def insert_products(products):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO products (name, price, stock, imageUrl, desc, category, rating) VALUES (?, ?, ?, ?, ?, ?, ?)",
        [
            (p["name"], p["price"], p["stock"], p["imageUrl"], p["desc"], p["category"], p["rating"])
            for p in products
        ]
    )

    conn.commit()
    conn.close()

    return products

def update_product(product_id, product):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE products 
    SET name=?, price=?, stock=?, imageUrl=?, desc=?, category=?, rating=?
                   where id = ?
                   """,(
                       product["name"],
                       product["price"],
                       product["stock"],
                       product["imageUrl"],
                       product["desc"],
                       product["category"],
                       product["rating"],
                       product_id
                   ))

    conn.commit()
    conn.close()


def delete_product(product_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
                   DELETE FROM products where id = ?
                   """,(
                       product_id,
                   ))

    conn.commit()
    conn.close()


def delete_all_products():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM products")

    conn.commit()
    conn.close()