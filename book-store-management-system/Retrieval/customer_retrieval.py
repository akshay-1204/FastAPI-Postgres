from Database.connection import get_connection

def get_all_customers():
    """Retrieves all customers from the database."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM customers")

            customers = cur.fetchall()
    
    for customer in customers:
        print(f"Customer ID: {customer[0]}, Name: {customer[1]}, Email: {customer[2]}, Phone: {customer[3]}")

    return customers

def get_customer_by_id(customer_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM customers WHERE id = %s",
                (customer_id,)
            )

            customer = cur.fetchone()

    if customer:
        print(customer)
    else:
        print("Customer not found.")

def get_customer_by_email(email):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM customers WHERE email = %s", (email,))

            customer = cur.fetchone()

    if customer:
        print(customer)
    else:
        print("Customer not found.")

def get_total_orders_by_customer(customer_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    c.id AS customer_id,
                    c.name AS customer_name,
                    COUNT(o.id) AS total_orders
                FROM customers c
                LEFT JOIN orders o
                    ON c.id = o.customer_id
                WHERE c.id = %s
                GROUP BY c.id, c.name
                """,
                (customer_id,)
            )

            result = cur.fetchone()

    if result:
        print(result)
    else:
        print("Customer not found.")

    return result


def get_total_spent_by_customer(customer_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    c.id AS customer_id,
                    c.name AS customer_name,
                    COALESCE(SUM(o.total_amount), 0) AS total_spent
                FROM customers c
                LEFT JOIN orders o
                    ON c.id = o.customer_id
                WHERE c.id = %s
                GROUP BY c.id, c.name
                """,
                (customer_id,)
            )

            result = cur.fetchone()

    if result:
        print(result)
    else:
        print("Customer not found.")

    return result

