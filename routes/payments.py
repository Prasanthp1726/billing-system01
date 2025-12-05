from flask import Blueprint, request, jsonify
from backend.models import db, Payment, Invoice

bp = Blueprint("payments", __name__, url_prefix="/api/payments")

@bp.route("", methods=["GET"])
def list_payments():
    payments = Payment.query.order_by(Payment.id.desc()).all()
    return jsonify([{
        "id": p.id,
        "invoice_id": p.invoice_id,
        "amount": float(p.amount),
        "date": p.date.isoformat() if p.date else None
    } for p in payments])

@bp.route("", methods=["POST"])
def add_payment():
    data = request.get_json() or {}
    try:
        amount = float(data.get("amount", 0))
    except (TypeError, ValueError):
        amount = 0
    invoice_id = data.get("invoice_id")
    date = data.get("date")  # Expect YYYY-MM-DD

    if amount <= 0 or not date:
        return jsonify({"error": "amount > 0 and date are required"}), 400

    p = Payment(amount=amount, invoice_id=invoice_id, date=date)
    db.session.add(p)

    # Optional: update invoice status to PAID when fully paid
    if invoice_id:
        inv = Invoice.query.get(invoice_id)
        if inv:
            paid_sum = sum(x.amount for x in Payment.query.filter_by(invoice_id=invoice_id).all()) + amount
            if paid_sum >= (inv.grand_total or 0):
                inv.status = "PAID"

    db.session.commit()
    return jsonify({"message": "created", "id": p.id}), 201
