from Database.connection import get_connection


def get_book_details_with_author_category(book_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    b.id AS book_id,
                    b.title AS book_title,
                    b.isbn,
                    b.price,
                    b.stock,
                    a.name AS author_name,
                    c.name AS category_name
                FROM books b
                INNER JOIN authors a
                    ON b.author_id = a.id
                INNER JOIN categories c
                    ON b.category_id = c.id
                WHERE b.id = %s
                """,
                (book_id,)
            )

            book = cur.fetchone()

    if book:
        print(book)
    else:
        print("Book not found.")

    return book


def get_order_with_items(order_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    o.id AS order_id,
                    o.customer_id,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    oi.id AS order_item_id,
                    oi.book_id,
                    oi.quantity,
                    oi.price
                FROM orders o
                INNER JOIN order_items oi
                    ON o.id = oi.order_id
                WHERE o.id = %s
                """,
                (order_id,)
            )

            order_items = cur.fetchall()

    if order_items:
        for item in order_items:
            print(item)
    else:
        print("Order not found.")

    return order_items


def get_customer_order_history(customer_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    c.id AS customer_id,
                    c.name AS customer_name,
                    o.id AS order_id,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    o.shipping_address
                FROM customers c
                INNER JOIN orders o
                    ON c.id = o.customer_id
                WHERE c.id = %s
                ORDER BY o.order_date DESC
                """,
                (customer_id,)
            )

            orders = cur.fetchall()

    if orders:
        for order in orders:
            print(order)
    else:
        print("No orders found for this customer.")

    return orders


def get_all_orders_with_customer_name():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    o.id AS order_id,
                    c.name AS customer_name,
                    o.order_date,
                    o.status,
                    o.total_amount,
                    o.shipping_address
                FROM orders o
                INNER JOIN customers c
                    ON o.customer_id = c.id
                ORDER BY o.order_date DESC
                """
            )

            orders = cur.fetchall()

    if orders:
        for order in orders:
            print(order)
    else:
        print("No orders found.")

    return orders