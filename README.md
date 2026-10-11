# FastAPI + PostgreSQL Projects Collection

A showcase of production-ready REST APIs built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**.

---

## Included Projects

### 1. [Vehicle Management System](./vehicle-management-system/)
* **Features**: Multi-tenant fleet management, customer data isolation, role-based access control (`customer` vs `admin`), vehicle tracking, insurance policies, maintenance records, replacement parts cost calculations, and analytical reports.
* **Architecture**: FastAPI, SQLAlchemy, PostgreSQL, Alembic migrations, Pytest suite (24 passing tests), and Streamlit interactive frontend.

### 2. [Blog Management API](./blogs-app/)
* **Features**: User authentication with password hashing (bcrypt), JWT access tokens, and CRUD operations for published blogs.
* **Architecture**: FastAPI, SQLAlchemy, PostgreSQL, and Pydantic schemas.

### 3. [Book Store Management System](./book-store-management-system/)
* **Features**: Comprehensive bookstore operations including Authors, Books, Categories, Customers, Orders, and Order Items with relational joins and analytics.
* **Architecture**: FastAPI, PostgreSQL, SQLAlchemy ORM, modular CRUD operations, and advanced SQL reporting.

---

## Setup & Running

Each subproject includes its own:
- `requirements.txt` with all required dependencies
- `.env.example` template for database configuration
- `README.md` with setup instructions

Clone the repository:
```bash
git clone https://github.com/akshay-1204/FastAPI-Postgres.git
cd FastAPI-Postgres
```
