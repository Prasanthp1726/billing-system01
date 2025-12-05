from flask import Blueprint, request, jsonify
from backend.models import db, Product

bp = Blueprint("products", __name__, url_prefix="/api/products")

@bp.route("", methods=["GET"])
def list_products():
    products = Product.query.order_by(Product.id.desc()).all()
    return jsonify([{
        "id": p.id, "name": p.name, "sku": getattr(p, "sku", None),
        "price": float(p.price), "stock": int(getattr(p, "stock", 0))
    } for p in products])

@bp.route("", methods=["POST"])
def add_product():
    data = request.get_json() or {}
    name = data.get("name")
    price = data.get("price")
    if not name or price is None:
        return jsonify({"error": "name and price required"}), 400
    product = Product(
        name=name,
        sku=data.get("sku"),
        price=float(price),
        stock=int(data.get("stock", 0)),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "created", "id": product.id}), 201

@bp.route("/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "deleted"})
