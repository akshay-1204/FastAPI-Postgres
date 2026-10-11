from app.models import User
from app.utils import hash_password


def test_register_success(client):
    payload = {
        "full_name": "Charlie Daniels",
        "email": "charlie@example.com",
        "password": "Password123!",
        "role": "customer"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "charlie@example.com"
    assert data["full_name"] == "Charlie Daniels"
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    payload = {
        "full_name": "Duplicate User",
        "email": "duplicate@example.com",
        "password": "Password123!",
        "role": "customer"
    }
    first_res = client.post("/auth/register", json=payload)
    assert first_res.status_code == 201

    second_res = client.post("/auth/register", json=payload)
    assert second_res.status_code == 409
    assert "already registered" in second_res.json()["detail"]


def test_register_short_password(client):
    payload = {
        "full_name": "Short Password",
        "email": "short@example.com",
        "password": "short",
        "role": "customer"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client, user_a):
    response = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "AliceSecure123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "customer"


def test_login_invalid_password(client, user_a):
    response = client.post(
        "/auth/login",
        data={"username": "alice@example.com", "password": "WrongPassword999!"}
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={"username": "ghost@example.com", "password": "Password123!"}
    )
    assert response.status_code == 401


def test_get_me(client, headers_a, user_a):
    response = client.get("/auth/me", headers=headers_a)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_a.email
    assert data["id"] == user_a.id


def test_inactive_user_rejected(client, db_session):
    inactive = User(
        full_name="Inactive Person",
        email="inactive@example.com",
        hashed_password=hash_password("Inactive123!"),
        role="customer",
        is_active=False
    )
    db_session.add(inactive)
    db_session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "inactive@example.com", "password": "Inactive123!"}
    )
    assert response.status_code == 403
    assert "Inactive user" in response.json()["detail"]
