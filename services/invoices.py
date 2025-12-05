from backend.db.connection import get_db
from backend.services.products import decrement_stock
from backend.services.utils import calculate_totals

def create_invoice(customer_id, items, tax_rate=0.0, discount_rate=0.0):
    # items: list of {product_id, qty, unit_price}
    totals = calculate_totals(items, tax_rate, discount_rate)

    conn = get_db()
    cur = conn.cursor()

    # Check stock and lock rows
    for it in items:
        ok = decrement_stock(it["product_id"], it["qty"])
        if not ok:
            conn.rollback()
            cur.close()
            conn.close()
            raise ValueError(f"Insufficient stock for product {it['product_id']}")

    cur.execute("""
        INSERT INTO invoices (customer_id, subtotal, tax_total, discount_total, grand_total, status)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
    """, (customer_id, totals["subtotal"], totals["tax_total"], totals["discount_total"], totals["grand_total"], "UNPAID"))
    invoice_id = cur.fetchone()[0]

    for it in items:
        line_total = round(it["qty"] * it["unit_price"], 2)
        cur.execute("""
            INSERT INTO invoice_items (invoice_id, product_id, qty, unit_price, line_total)
            VALUES (%s, %s, %s, %s, %s);
        """, (invoice_id, it["product_id"], it["qty"], it["unit_price"], line_total))

    conn.commit()
    cur.close()
    conn.close()
    return invoice_id

def list_invoices():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id, c.name, i.grand_total, i.status
        FROM invoices i JOIN customers c ON c.id = i.customer_id
        ORDER BY i.id DESC;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "customer_name": r[1], "grand_total": float(r[2]), "status": r[3]} for r in rows]
