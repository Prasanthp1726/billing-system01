from flask import Blueprint, request, jsonify
from backend.models import db, Invoice, InvoiceItem, Product

bp = Blueprint("invoices", __name__, url_prefix="/api/invoices")

@bp.route("", methods=["GET"])
def list_invoices():
    invoices = Invoice.query.order_by(Invoice.id.desc()).all()
    result = []
    for inv in invoices:
        result.append({
            "id": inv.id,
            "customer_id": inv.customer_id,
            "customer_name": inv.customer.name if getattr(inv, "customer", None) else "-",
            "grand_total": float(inv.grand_total or 0),
            "status": inv.status or "UNPAID"
        })
    return jsonify(result)

@bp.route("", methods=["POST"])
def create_invoice():
    data = request.get_json() or {}
    customer_id = data.get("customer_id")
    items_data = data.get("items", [])
    tax_rate = float(data.get("tax_rate", 0))
    discount_rate = float(data.get("discount_rate", 0))

    if not customer_id or not items_data:
        return jsonify({"error": "customer_id and items required"}), 400

    subtotal = 0.0
    item_rows = []
    for it in items_data:
        pid = int(it.get("product_id", 0))
        qty = int(it.get("qty", 0))
        price = float(it.get("price", 0))
        if pid <= 0 or qty <= 0:
            return jsonify({"error": "Each item needs product_id and qty > 0"}), 400
        prod = Product.query.get(pid)
        if not prod:
            return jsonify({"error": f"product {pid} not found"}), 404
        unit_price = price if price > 0 else float(prod.price)
        line_total = unit_price * qty
        subtotal += line_total
        item_rows.append({"product_id": pid, "qty": qty, "unit_price": unit_price, "line_total": line_total})

    tax_total = subtotal * tax_rate / 100.0
    discount_total = subtotal * discount_rate / 100.0
    grand_total = subtotal + tax_total - discount_total

    inv = Invoice(
        customer_id=customer_id,
        subtotal=subtotal,
        tax_total=tax_total,
        discount_total=discount_total,
        grand_total=grand_total,
        status="UNPAID",
    )
    db.session.add(inv)
    db.session.flush()

    for row in item_rows:
        ii = InvoiceItem(
            invoice_id=inv.id,
            product_id=row["product_id"],
            quantity=row["qty"],
            unit_price=row["unit_price"],
            line_total=row["line_total"],
        )
        db.session.add(ii)

    db.session.commit()
    return jsonify({"message": "created", "id": inv.id, "grand_total": grand_total}), 201
