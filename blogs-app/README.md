Blog Management API
===================

A RESTful Blog API built with FastAPI, PostgreSQL, and SQLAlchemy.

Features
--------
- User registration and authentication with JWT and bcrypt
- CRUD operations for blogs
- Relationship between users and blogs
- Safe configuration with .env and .env.example

Setup
-----
1. pip install -r requirements.txt
2. Copy .env.example to .env and configure DATABASE_URL
3. uvicorn main:app --reload
