from backend.db.connection import get_db

def customer_balance_summary():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
      SELECT c.id, c.name,
        COALESCE((SELECT SUM(grand_total) FROM invoices i WHERE i.customer_id = c.id),0) AS invoiced,
        COALESCE((SELECT SUM(amount) FROM payments p JOIN invoices i ON i.id = p.invoice_id WHERE i.customer_id = c.id),0) AS paid
      FROM customers c WHERE c.is_deleted = FALSE;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = []
    for r in rows:
        invoiced = float(r[2])
        paid = float(r[3])
        result.append({"customer_id": r[0], "name": r[1], "invoiced_total": invoiced, "payments_total": paid, "outstanding": round(invoiced - paid, 2)})
    return result

def sales_summary(start_date=None, end_date=None):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
      SELECT COUNT(*), COALESCE(SUM(grand_total),0), COALESCE(SUM(tax_total),0)
      FROM invoices
      WHERE ($1::timestamp IS NULL OR created_at >= $1)
        AND ($2::timestamp IS NULL OR created_at <= $2);
    """.replace("$", "%"), (start_date, end_date))
    count, total_sales, total_tax = cur.fetchone()
    avg_invoice = float(total_sales) / count if count else 0.0
    cur.close()
    conn.close()
    return {"count": count, "total_sales": float(total_sales), "total_tax": float(total_tax), "avg_invoice": round(avg_invoice, 2)}

def top_products():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
      SELECT p.id, p.name, SUM(ii.qty) AS qty_sold, SUM(ii.line_total) AS revenue
      FROM invoice_items ii JOIN products p ON p.id = ii.product_id
      GROUP BY p.id, p.name ORDER BY qty_sold DESC LIMIT 10;
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"product_id": r[0], "name": r[1], "qty_sold": int(r[2]), "revenue": float(r[3])} for r in rows]

def customer_statement(customer_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
      SELECT 'INVOICE' AS type, id, grand_total AS amount, created_at
      FROM invoices WHERE customer_id = %s
      UNION ALL
      SELECT 'PAYMENT' AS type, p.id, p.amount, p.created_at
      FROM payments p JOIN invoices i ON i.id = p.invoice_id
      WHERE i.customer_id = %s
      ORDER BY created_at ASC;
    """, (customer_id, customer_id))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    running = 0.0
    statement = []
    for t, id_, amount, dt in rows:
        running += amount if t == "INVOICE" else -amount
        statement.append({"type": t, "id": id_, "amount": float(amount), "date": dt.isoformat(), "running_balance": round(running, 2)})
    return statement
