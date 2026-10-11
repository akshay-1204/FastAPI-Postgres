from Database.connection import get_connection


def add_order(
    customer_id: int,
    status: str,
    total_amount: float,
    shipping_address: str
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO orders
                (customer_id, status, total_amount, shipping_address)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    customer_id,
                    status,
                    total_amount,
                    shipping_address
                )
            )

    print(f"Successfully added order for customer ID: {customer_id}")


def insert_orders():

    no_of_orders = int(input("Enter number of orders you want to add: "))

    for i in range(no_of_orders):

        print(f"\nEnter Order {i + 1} details")

        customer_id = int(input("Enter customer ID: "))
        status = input("Enter order status: ")
        total_amount = float(input("Enter total amount: "))
        shipping_address = input("Enter shipping address: ")

        add_order(
            customer_id,
            status,
            total_amount,
            shipping_address
        )