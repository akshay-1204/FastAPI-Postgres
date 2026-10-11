from Database.connection import get_connection


def add_category(name: str, description: str):
    """Insert one category into the categories table."""

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO categories
                (name, description)
                VALUES (%s, %s)
                """,
                (name, description)
            )

    print(f"Successfully added category: {name}")


def insert_categories():

    no_of_categories = int(
        input("Enter number of categories you want to add: ")
    )

    for i in range(no_of_categories):

        print(f"\nEnter Category {i + 1} details")

        name = input("Enter category name: ")
        description = input("Enter category description: ")

        add_category(name, description)