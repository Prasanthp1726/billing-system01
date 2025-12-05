# backend/routes/customers.py
from flask import Blueprint, request, jsonify
from backend.models import db
from backend.models.customer import Customer
import sqlalchemy

bp = Blueprint("customers", __name__, url_prefix="/api/customers")

@bp.route("", methods=["GET"])
def list_customers():
  rows = Customer.query.filter_by(is_deleted=False).order_by(Customer.id.desc()).all()
  return jsonify([
    {"id": c.id, "name": c.name, "email": c.email, "phone": c.phone}
    for c in rows
  ])

@bp.route("", methods=["POST"])
def add_customer():
  try:
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not name:
      return jsonify({"error": "Name is required"}), 400

    c = Customer(name=name, email=email, phone=phone)
    db.session.add(c)
    db.session.commit()
    return jsonify({"message": "Customer added", "id": c.id}), 201

  except Exception as e:
    db.session.rollback()
    print("Add customer error:", e)  # see exact error in terminal
    return jsonify({"error": str(e)}), 500

@bp.route("/<int:cid>", methods=["DELETE"])
def delete_customer(cid):
  c = Customer.query.get(cid)
  if not c:
    return jsonify({"error": "Customer not found"}), 404
  c.is_deleted = True
  db.session.commit()
  return jsonify({"message": "Deleted"})
