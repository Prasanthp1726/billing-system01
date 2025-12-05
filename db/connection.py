import psycopg2

def get_db():
    return psycopg2.connect(
        dbname="billing_system",
        user="billing_user",
        password="billing_pass",
        host="localhost",
        port="5432",
    )
