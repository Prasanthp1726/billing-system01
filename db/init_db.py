from backend.db.connection import get_db
from backend.app import app, db

with app.app_context():
    db.create_all()


def init_db():
    conn = get_db()
    cur = conn.cursor()
    with open("backend/db/schema.sql", "r") as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()

db.init_app(app)
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(...)