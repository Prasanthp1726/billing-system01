from backend.db.connection import get_db

def add_product(data):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, price, stock) VALUES (%s, %s, %s);",
                (data["name"], float(data["price"]), int(data["stock"])))
    conn.commit()
    cur.close()
    conn.close()

def list_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products WHERE is_deleted = FALSE;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1], "price": float(r[2]), "stock": r[3]} for r in rows]

def delete_product(product_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE products SET is_deleted = TRUE WHERE id = %s;", (product_id,))
    conn.commit()
    cur.close()
    conn.close()

def decrement_stock(product_id, qty):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE products SET stock = stock - %s WHERE id = %s AND stock >= %s;",
                (qty, product_id, qty))
    updated = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    return updated > 0
