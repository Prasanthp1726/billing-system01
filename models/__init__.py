# backend/models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models AFTER db is defined
from backend.models.customer import Customer
from backend.models.product import Product
from backend.models.invoice import Invoice
from backend.models.invoice_item import InvoiceItem
from backend.models.payment import Payment

__all__ = ["db", "Customer", "Product", "Invoice", "InvoiceItem", "Payment"]
