# tests/db_check.py (temporary file)
from backend.app import app
from backend.models import db

def check_db():
    with app.app_context():
        # 1) Low-level ping
        conn = db.engine.connect()
        result = conn.execute(db.text("SELECT version();"))
        print("PostgreSQL version:", result.fetchone()[0])
        conn.close()

        # 2) Verify current database
        result = db.session.execute(db.text("SELECT current_database();"))
        print("Connected to DB:", result.scalar())

        # 3) Verify tables exist (SQLAlchemy metadata)
        insp = db.inspect(db.engine)
        print("Tables:", insp.get_table_names())

if __name__ == "__main__":
    check_db()
