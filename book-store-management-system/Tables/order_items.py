from Database.connection import get_connection


def create_order_items_table():

    with get_connection() as conn:

        with conn.cursor() as cur:

            cur.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INT REFERENCES orders(id),
                    book_id INT REFERENCES books(id),
                    quantity INT NOT NULL,
                    price DECIMAL(10,2) NOT NULL
                )
            """)

    print("Order Items Table created successfully.")