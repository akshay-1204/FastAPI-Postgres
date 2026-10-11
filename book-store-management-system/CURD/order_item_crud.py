from Database.connection import get_connection


def add_order_item(
    order_id: int,
    book_id: int,
    quantity: int,
    price: float
):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO order_items
                (order_id, book_id, quantity, price)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    order_id,
                    book_id,
                    quantity,
                    price
                )
            )

    print(
        f"Successfully added book ID {book_id} "
        f"to order ID {order_id}"
    )


def insert_order_items():

    no_of_order_items = int(
        input("Enter number of order items you want to add: ")
    )

    for i in range(no_of_order_items):

        print(f"\nEnter Order Item {i + 1} details")

        order_id = int(input("Enter order ID: "))
        book_id = int(input("Enter book ID: "))
        quantity = int(input("Enter quantity: "))
        price = float(input("Enter price: "))

        add_order_item(
            order_id,
            book_id,
            quantity,
            price
        )