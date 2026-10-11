from Database.connection import get_connection

def create_categories_table():
    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
                Create Table IF NOT EXISTS categories(
                    id serial Primary Key,
                    name varchar(100) UNIQUE NOT NULL,
                    description Text
                ) 
            """)

    print("Categories Table created successfully.")