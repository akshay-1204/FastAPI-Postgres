from Database.connection import get_connection


def get_orders_by_status(status):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM orders WHERE status = %s",
                (status,)
            )

            orders = cur.fetchall()

    if orders:
        for order in orders:
            print(order)
    else:
        print("No orders found with this status.")

    return orders


def get_orders_by_customer(customer_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM orders WHERE customer_id = %s",
                (customer_id,)
            )

            orders = cur.fetchall()

    if orders:
        for order in orders:
            print(order)
    else:
        print("No orders found for this customer.")

    return orders


def get_orders_between_dates(start_date, end_date):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT * FROM orders
                WHERE order_date >= %s
                  AND order_date < %s
                """,
                (start_date, end_date)
            )

            orders = cur.fetchall()

    if orders:
        for order in orders:
            print(order)
    else:
        print("No orders found in this date range.")

    return orders  

def get_orders_paginated(limit, offset):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM orders
                ORDER BY id
                LIMIT %s
                OFFSET %s
                """,
                (limit, offset)
            )

            orders = cur.fetchall()

    if orders:
        for order in orders:
            print(order)
    else:
        print("No orders found.")

    return orders