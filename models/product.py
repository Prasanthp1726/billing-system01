from backend.models import db

class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(60))
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)

    # Relationship: one product can appear in many invoice items
    items = db.relationship("InvoiceItem", back_populates="product")

    def __repr__(self):
        return f"<Product {self.id} {self.name}>"
