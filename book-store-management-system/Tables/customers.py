from Database.connection import get_connection

def create_customers_table():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
            Create Table IF NOT EXISTS customers(
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(15),
            address TEXT,
            created_at TIMESTAMP DEFAULT NOW()
            )
            """)

    print("Customers Table created successfully.")