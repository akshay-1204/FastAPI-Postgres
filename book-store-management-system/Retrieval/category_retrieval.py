from Database.connection import get_connection


def get_all_categories():

    """Retrieves all categories from the database."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT * FROM categories")

            categories = cur.fetchall()

    for category in categories:
        print(category)

    return categories

def get_revenue_by_category():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    c.id AS category_id,
                    c.name AS category_name,
                    SUM(oi.quantity * oi.price) AS total_revenue
                FROM categories c
                INNER JOIN books b
                    ON c.id = b.category_id
                INNER JOIN order_items oi
                    ON b.id = oi.book_id
                GROUP BY c.id, c.name
                ORDER BY total_revenue DESC
                """
            )

            categories = cur.fetchall()

    if categories:
        for category in categories:
            print(category)
    else:
        print("No revenue data found.")

    return categories
    
def get_average_book_price_by_category():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    c.id AS category_id,
                    c.name AS category_name,
                    ROUND(AVG(b.price), 2) AS average_book_price
                FROM categories c
                INNER JOIN books b
                    ON c.id = b.category_id
                GROUP BY c.id, c.name
                ORDER BY average_book_price DESC
                """
            )

            categories = cur.fetchall()

    if categories:
        for category in categories:
            print(category)
    else:
        print("No category price data found.")

    return categories