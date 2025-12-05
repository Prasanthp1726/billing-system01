# backend/config.py
import os

DB_URL = os.getenv(
    "DB_URL",
    "postgresql://billing_user:StrongPass123@localhost:5432/billing_system"
)

API_PREFIX = "/api"
SQLALCHEMY_DATABASE_URI = DB_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False
