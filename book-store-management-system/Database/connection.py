import os
from pathlib import Path
import psycopg
from dotenv import load_dotenv

# Load environment variables from .env in project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

DB_NAME = os.getenv("DB_NAME", "bookstore_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "akshay1204#")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Construct DB_PARAMS or read directly from environment
DB_PARAMS = os.getenv(
    "DB_PARAMS",
    f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
)

def get_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    return psycopg.connect(DB_PARAMS)
