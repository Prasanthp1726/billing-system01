from flask import Flask, render_template
from pathlib import Path
import backend.config as config
from backend.models import db
import sqlalchemy   # <-- add this import

# Import blueprints
from backend.routes.customers import bp as customers_bp
from backend.routes.products import bp as products_bp
from backend.routes.invoices import bp as invoices_bp
from backend.routes.payments import bp as payments_bp
from backend.routes.reports import bp as reports_bp

# Setup Flask app
BASE_DIR = Path(__file__).parent
app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = config.SQLALCHEMY_TRACK_MODIFICATIONS

# Attach SQLAlchemy
db.init_app(app)

# Page routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard_page():
    return render_template("pages/dashboard.html")

@app.route("/customers")
def customers_page():
    return render_template("pages/customers.html")

@app.route("/products")
def products_page():
    return render_template("pages/products.html")

@app.route("/invoices")
def invoices_page():
    return render_template("pages/invoices.html")

@app.route("/payments")
def payments_page():
    return render_template("pages/payments.html")

@app.route("/reports")
def reports_page():
    return render_template("pages/reports.html")

# ✅ Health check route to confirm DB connection
@app.route("/check-db")
def check_db():
    try:
        version = db.session.execute(sqlalchemy.text("SELECT version();")).scalar()
        current_db = db.session.execute(sqlalchemy.text("SELECT current_database();")).scalar()
        return f"Connected to {current_db}, version: {version}"
    except Exception as e:
        return f"DB connection error: {e}", 500

# Attach API blueprints
app.register_blueprint(customers_bp)
app.register_blueprint(products_bp)
app.register_blueprint(invoices_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(reports_bp)

# Run server
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="127.0.0.1", port=8000, debug=True)
