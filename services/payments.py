from backend.db.connection import get_db

def add_payment(data):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO payments (invoice_id, amount) VALUES (%s, %s);",
                (data.get("invoice_id"), float(data["amount"])))
    # Update invoice status if linked
    if data.get("invoice_id"):
        invoice_id = int(data["invoice_id"])
        cur.execute("SELECT grand_total FROM invoices WHERE id = %s;", (invoice_id,))
        grand_total = float(cur.fetchone()[0])
        cur.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE invoice_id = %s;", (invoice_id,))
        paid = float(cur.fetchone()[0])
        status = "UNPAID"
        if paid == 0:
            status = "UNPAID"
        elif paid < grand_total:
            status = "PARTIALLY_PAID"
        else:
            status = "PAID"
        cur.execute("UPDATE invoices SET status = %s WHERE id = %s;", (status, invoice_id))
    conn.commit()
    cur.close()
    conn.close()

def list_payments():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, invoice_id, amount, created_at FROM payments ORDER BY id DESC;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "invoice_id": r[1], "amount": float(r[2]), "date": r[3].isoformat()} for r in rows]
