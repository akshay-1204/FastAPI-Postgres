from Database.connection import get_connection

def create_orders_table():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
            Create table if not exists orders(
                id SERIAL PRIMARY KEY,
                customer_id INT REFERENCES customers(id),
                order_date TIMESTAMP DEFAULT NOW(),
                status VARCHAR(20) NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                shipping_address TEXT
            )

            """)

    print("Orders Table created successfully.")