from Database.connection import get_connection


def get_best_selling_books(limit):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    b.id AS book_id,
                    b.title,
                    SUM(oi.quantity) AS total_quantity_sold
                FROM books b
                INNER JOIN order_items oi
                    ON b.id = oi.book_id
                GROUP BY b.id, b.title
                ORDER BY total_quantity_sold DESC
                LIMIT %s
                """,
                (limit,)
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No sales found.")

    return books

def get_monthly_order_summary():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    DATE_TRUNC('month', order_date) AS order_month,
                    COUNT(*) AS total_orders,
                    SUM(total_amount) AS total_revenue
                FROM orders
                GROUP BY DATE_TRUNC('month', order_date)
                ORDER BY order_month
                """
            )

            summary = cur.fetchall()

    if summary:
        for row in summary:
            print(row)
    else:
        print("No order data found.")

    return summary