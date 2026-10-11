from Database.connection import get_connection

def add_customer(name:str, email:str, phone:str, address:str):
    """Adds a new customer to the database."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)", (name, email, phone, address))
            
            print(f"Successfully added customer: {name}")

def insert_customers():

    no_of_customers = int(
        input("Enter number of customers you want to add: ")
    )

    for i in range(no_of_customers):

        print(f"\nEnter Customer {i + 1} details")

        name = input("Enter customer name: ")
        email = input("Enter customer email: ")
        phone = input("Enter customer phone: ")
        address = input("Enter customer address: ")

        add_customer(name, email, phone, address)