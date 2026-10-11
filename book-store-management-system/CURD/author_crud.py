from Database.connection import get_connection


def add_author(name: str, email: str, country: str):
    """Insert one author into the authors table."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO authors
                (name, email, country)
                VALUES (%s, %s, %s)
                """,
                (name, email, country)
            )

    print(f"Successfully added author: {name}")


def insert_authors():

    no_of_authors = int(
        input("Enter number of authors you want to add: ")
    )

    for i in range(no_of_authors):

        print(f"\nEnter Author {i + 1} details")

        name = input("Enter author name: ")
        email = input("Enter author email: ")
        country = input("Enter author country: ")

        add_author(name, email, country)