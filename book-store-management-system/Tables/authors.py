from Database.connection import get_connection

def create_authors_table():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute("""
            Create Table IF NOT EXISTS authors(
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            country VARCHAR(50),
            created_at TIMESTAMP DEFAULT NOW()
            )
            """)
    print(f"Authors Table created successfully.")

    
