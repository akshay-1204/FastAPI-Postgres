from Database.connection import get_connection


def add_book(
    author_id: int,
    category_id: int,
    title: str,
    isbn: str,
    price: float,
    stock: int,
    published_year: int
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books
                (author_id, category_id, title, isbn, price, stock, published_year)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    author_id,
                    category_id,
                    title,
                    isbn,
                    price,
                    stock,
                    published_year
                )
            )

    print(f"Successfully added book: {title}")


def insert_books():

    no_of_books = int(input("Enter number of books you want to add: "))

    for i in range(no_of_books):

        print(f"\nEnter Book {i + 1} details")

        author_id = int(input("Enter author ID: "))
        category_id = int(input("Enter category ID: "))
        title = input("Enter book title: ")
        isbn = input("Enter ISBN: ")
        price = float(input("Enter book price: "))
        stock = int(input("Enter stock quantity: "))
        published_year = int(input("Enter published year: "))

        add_book(
            author_id,
            category_id,
            title,
            isbn,
            price,
            stock,
            published_year
        )