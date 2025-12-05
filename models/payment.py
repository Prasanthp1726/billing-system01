from backend.models import db
from sqlalchemy.sql import func

class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    # Store date as DATE; alternatively use db.DateTime with default=func.now()
    date = db.Column(db.Date, nullable=False)
