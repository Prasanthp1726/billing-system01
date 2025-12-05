from backend.db.connection import get_db

def add_customer(data):
    """
    Insert a customer and return the new record's id.
    Required: name
    Optional: email, phone
    """
    # Basic validation
    name = (data or {}).get("name")
    email = (data or {}).get("email")
    phone = (data or {}).get("phone")

    if not name or not isinstance(name, str):
        raise ValueError("Field 'name' is required and must be a string")

    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()

        # Insert record
        cur.execute(
            "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s) RETURNING id;",
            (name, email, phone),
        )
        new_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        return {"id": new_id, "name": name, "email": email, "phone": phone}

    except Exception as e:
        # Roll back on any error
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def list_customers():
    """
    Return active (not soft-deleted) customers.
    """
    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, email, phone FROM customers WHERE is_deleted = FALSE ORDER BY id ASC;"
        )
        rows = cur.fetchall()
        cur.close()
        return [{"id": r[0], "name": r[1], "email": r[2], "phone": r[3]} for r in rows]
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def delete_customer(customer_id):
    """
    Soft delete a customer by id. Returns number of affected rows.
    """
    if not isinstance(customer_id, int):
        raise ValueError("customer_id must be an integer")

    conn = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("UPDATE customers SET is_deleted = TRUE WHERE id = %s;", (customer_id,))
        affected = cur.rowcount
        conn.commit()
        cur.close()
        return {"deleted": affected}
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()
