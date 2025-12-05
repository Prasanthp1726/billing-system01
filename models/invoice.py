# backend/models/invoice.py
from backend.models import db

class Invoice(db.Model):
    __tablename__ = "invoices"
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    subtotal = db.Column(db.Float, default=0)
    tax_total = db.Column(db.Float, default=0)
    discount_total = db.Column(db.Float, default=0)
    grand_total = db.Column(db.Float, default=0)
    status = db.Column(db.String(20), default="UNPAID")
    invoice_date = db.Column(db.Date, default=db.func.current_date)  # <-- add this

    customer = db.relationship("Customer", backref="invoices")
    items = db.relationship("InvoiceItem", backref="invoice", cascade="all, delete-orphan")
