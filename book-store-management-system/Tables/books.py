from Database.connection import get_connection

def create_books_table():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
            Create table if not exists books(
                id serial Primary Key,
                author_id int REFERENCES authors(id),
                category_id INT REFERENCES categories(id),
                title VARCHAR(200) NOT NULL,
                isbn VARCHAR(20) UNIQUE NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                stock INT DEFAULT 0,
                published_year INT,
                created_at TIMESTAMP DEFAULT NOW() 
            )

            """)

    print("Books Table created successfully.")