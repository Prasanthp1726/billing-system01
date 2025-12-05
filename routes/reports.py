from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.models import db, Customer, Product, Invoice, InvoiceItem, Payment
from flask import request, jsonify
from backend.models import db
import sqlalchemy

bp = Blueprint("reports", __name__, url_prefix="/api/reports")

@bp.route("/customer-balance", methods=["GET"])
def customer_balance():
    # Total invoiced per customer
    totals = db.session.query(
        Customer.id, Customer.name, func.coalesce(func.sum(Invoice.grand_total), 0.0)
    ).outerjoin(Invoice, Invoice.customer_id == Customer.id)\
     .group_by(Customer.id, Customer.name).all()

    # Total payments per customer via invoices
    pays = db.session.query(
        Customer.id, func.coalesce(func.sum(Payment.amount), 0.0)
    ).join(Invoice, Invoice.customer_id == Customer.id)\
     .outerjoin(Payment, Payment.invoice_id == Invoice.id)\
     .group_by(Customer.id).all()
    pay_map = {cid: float(total) for cid, total in pays}

    result = []
    for cid, name, inv_total in totals:
        paid = pay_map.get(cid, 0.0)
        balance = float(inv_total) - float(paid)
        result.append({"customer_id": cid, "customer": name, "invoiced": float(inv_total), "paid": float(paid), "balance": balance})
    return jsonify(result)

@bp.route("/sales-summary", methods=["GET"])
def sales_summary():
    total_sales = db.session.query(func.coalesce(func.sum(Invoice.grand_total), 0.0)).scalar() or 0.0
    invoice_count = db.session.query(func.count(Invoice.id)).scalar() or 0
    paid_total = db.session.query(func.coalesce(func.sum(Payment.amount), 0.0)).scalar() or 0.0
    return jsonify({"total_sales": float(total_sales), "invoice_count": int(invoice_count), "total_paid": float(paid_total)})

@bp.route("/top-products", methods=["GET"])
def top_products():
    rows = db.session.query(
        Product.name, func.coalesce(func.sum(InvoiceItem.quantity), 0)
    ).outerjoin(InvoiceItem, InvoiceItem.product_id == Product.id)\
     .group_by(Product.name).order_by(func.sum(InvoiceItem.quantity).desc()).limit(5).all()
    return jsonify([{"product": name, "qty_sold": int(qty)} for name, qty in rows])

@bp.route("/customer-statement")
def customer_statement():
    cid = request.args.get("customer_id", type=int)
    if not cid:
        return jsonify([])

    rows = db.session.execute(sqlalchemy.text("""
    SELECT i.invoice_date AS date,
       CONCAT('INV-', i.id) AS invoice,
       i.grand_total AS amount
    FROM invoices i
    WHERE i.customer_id = :cid
    ORDER BY i.invoice_date DESC
"""), {"cid": cid}).fetchall()


    return jsonify([
    {
        "date": r.date.strftime("%Y-%m-%d") if r.date else "-",
        "invoice": r.invoice or "-",
        "amount": float(r.amount) if r.amount is not None else 0
    }
    for r in rows
])
