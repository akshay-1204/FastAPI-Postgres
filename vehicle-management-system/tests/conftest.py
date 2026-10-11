import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.db import get_db
from app.main import app
from app.models import Customer, ServiceCenter, User
from app.utils import create_access_token, hash_password

test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    user = User(
        full_name="Admin Fleet Manager",
        email="admin@fleet.local",
        hashed_password=hash_password("AdminPass123!"),
        role="admin",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user):
    token = create_access_token({"sub": str(admin_user.id), "role": admin_user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_a(db_session):
    user = User(
        full_name="Alice Owner",
        email="alice@example.com",
        hashed_password=hash_password("AliceSecure123!"),
        role="customer",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    customer = Customer(
        user_id=user.id,
        full_name="Alice Owner",
        email="alice@example.com",
        phone="555-0101",
        address="100 First St"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def headers_a(user_a):
    token = create_access_token({"sub": str(user_a.id), "role": user_a.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_b(db_session):
    user = User(
        full_name="Bob Driver",
        email="bob@example.com",
        hashed_password=hash_password("BobSecure123!"),
        role="customer",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    customer = Customer(
        user_id=user.id,
        full_name="Bob Driver",
        email="bob@example.com",
        phone="555-0202",
        address="200 Second Ave"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def headers_b(user_b):
    token = create_access_token({"sub": str(user_b.id), "role": user_b.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def service_center(db_session):
    center = ServiceCenter(
        center_name="Central Automotive Hub",
        phone="555-0909",
        email="service@central.local",
        address="99 Industrial Pkwy",
        city="Metropolis",
        rating=4.8
    )
    db_session.add(center)
    db_session.commit()
    db_session.refresh(center)
    return center
