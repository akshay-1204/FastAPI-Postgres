from Database.connection import get_connection


def get_all_authors():

    """Retrieves all authors from the database."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT * FROM authors")

            authors = cur.fetchall()

    for author in authors:
        print(author)

    return authors


def get_author_by_id(author_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM authors WHERE id = %s",
                (author_id,)
            )

            author = cur.fetchone()

    if author:
        print(author)
    else:
        print("Author not found.")

def get_top_authors_by_sales(limit):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    a.id AS author_id,
                    a.name AS author_name,
                    SUM(oi.quantity) AS total_books_sold
                FROM authors a
                INNER JOIN books b
                    ON a.id = b.author_id
                INNER JOIN order_items oi
                    ON b.id = oi.book_id
                GROUP BY a.id, a.name
                ORDER BY total_books_sold DESC
                LIMIT %s
                """,
                (limit,)
            )

            authors = cur.fetchall()

    if authors:
        for author in authors:
            print(author)
    else:
        print("No sales data found.")

    return authors