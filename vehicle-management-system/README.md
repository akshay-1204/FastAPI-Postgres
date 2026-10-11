Vehicle Management System
=========================

Overview
--------
This is a secure, role-aware, multi-tenant vehicle management system built with FastAPI, SQLAlchemy, Alembic, and Streamlit.

All 5 core issues from the architecture review have been resolved:
1. User Data Security & Data Ownership:
   - Built-in role separation (Customer vs Admin).
   - Customers can only access, view, update, and delete their own customer record, vehicles, insurance policies, service records, and parts.
   - Admins can manage all fleet resources and external service centers.
   - Automated ownership verification on all resource routes.

2. Sensitive Environment & Git Protection:
   - Secret keys and database configurations are read from .env.
   - .gitignore excludes .env, caches, and test artifacts while explicitly tracking requirements.txt.
   - .env.example template provided with dummy variables.

3. Clean Dependency Management:
   - UTF-8 clean requirements.txt without pip commands or syntax errors.

4. Database Migrations via Alembic:
   - Alembic initialized and configured.
   - Initial version migration (001_initial_schema.py) included.
   - Supports seamless schema migration.

5. End-to-End Test Suite:
   - Comprehensive test suite in tests/ covering auth, authorization, ownership boundaries, and reporting with 100 percent pass rate.

Project Structure
-----------------
vechiles managing system/
  .env                  - Local environment configuration
  .env.example          - Template environment configuration
  .gitignore            - Git ignore rules
  requirements.txt      - Python dependencies list
  alembic.ini           - Alembic configuration file
  README.md             - Documentation
  alembic/
    env.py              - Migration environment runner
    script.py.mako      - Revision script template
    versions/
      001_initial_schema.py - Initial database migration
  app/
    database.py         - SQLAlchemy engine and session factory
    db.py               - Database session yield dependency
    models.py           - SQLAlchemy models with roles and relations
    schemas.py          - Pydantic v2 schemas and validation
    utils.py            - Password hashing (bcrypt) and JWT helpers
    dependencies.py     - Authentication and authorization guards
    main.py             - FastAPI application and router registration
    routers/
      auth.py           - Registration, JWT login, and current user
      customers.py      - Customer profile management with ownership checks
      vehicles.py       - Vehicle management with ownership checks
      insurance.py      - Insurance policy management with vehicle checks
      service_centers.py- Service center directory (admin restricted mutations)
      service_records.py- Service history with vehicle ownership guards
      vehicle_parts.py  - Parts tracking and automatic cost computation
      reports.py        - Scoped analytical aggregations
  frontend/
    streamlit_app.py    - Interactive Streamlit dashboard
  tests/
    conftest.py         - Pytest SQLite fixtures and client setup
    test_auth.py        - Authentication test cases
    test_customers.py   - Customer isolation test cases
    test_vehicles.py    - Vehicle ownership test cases
    test_insurance.py   - Insurance ownership and date validation tests
    test_service_records.py - Service record isolation tests
    test_vehicle_parts.py   - Vehicle parts and price computation tests
    test_service_centers.py - Role permissions tests
    test_reports.py     - Scoped analytical report tests

Installation and Setup
----------------------
1. Install dependencies:
   pip install -r requirements.txt

2. Run Database Migrations:
   alembic upgrade head

3. Start the FastAPI Backend:
   uvicorn app.main:app --reload --port 8000

   Interactive Swagger UI is accessible at:
   http://127.0.0.1:8000/docs

4. Start the Streamlit Frontend:
   streamlit run frontend/streamlit_app.py

5. Run Automated Tests:
   pytest tests -v
