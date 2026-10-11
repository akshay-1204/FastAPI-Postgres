from Database.connection import get_connection


def get_all_books():

    """Retrieves all books from the database."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT * FROM books")

            books = cur.fetchall()

    for book in books:
        print(book)

    return books


def get_book_by_id(book_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM books WHERE id = %s",
                (book_id,)
            )

            book = cur.fetchone()

    if book:
        print(book)
    else:
        print("Book not found.")


def get_book_by_isbn(isbn):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM books WHERE isbn = %s",
                (isbn,)
            )

            book = cur.fetchone()

    if book:
        print(book)
    else:
        print("Book not found.")

def search_books_by_title(keyword):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM books WHERE title LIKE %s",
                (f"%{keyword}%",)
            )

            books = cur.fetchall()

    for book in books:
        print(book)

    return books

def get_books_by_category(category_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM books WHERE category_id = %s",
                (category_id,)
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No books found for this category.")

    return books

def get_books_by_author(author_id):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM books WHERE author_id = %s",
                (author_id,)
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No books found for this author.")

    return books

def get_books_in_price_range(min_price, max_price):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT * FROM books
                WHERE price BETWEEN %s AND %s
                """,
                (min_price, max_price)
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No books found in this price range.")

    return books

def get_books_in_stock():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM books WHERE stock > 0"
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No books currently in stock.")

    return books

def get_out_of_stock_books():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT * FROM books WHERE stock = 0"
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No out-of-stock books found.")

    return books

def get_books_published_between(start_year, end_year):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT * FROM books
                WHERE published_year BETWEEN %s AND %s
                """,
                (start_year, end_year)
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No books found in this year range.")

    return books

def get_low_stock_books(threshold):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM books
                WHERE stock <= %s
                ORDER BY stock ASC
                """,
                (threshold,)
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No low-stock books found.")

    return books

def get_books_paginated(limit, offset):

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT *
                FROM books
                ORDER BY id
                LIMIT %s
                OFFSET %s
                """,
                (limit, offset)
            )

            books = cur.fetchall()

    if books:
        for book in books:
            print(book)
    else:
        print("No books found.")

    return books

