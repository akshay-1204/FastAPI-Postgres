def test_get_customers_scoped(client, headers_a, headers_b, admin_headers, user_a, user_b):
    res_a = client.get("/customers/", headers=headers_a)
    assert res_a.status_code == 200
    list_a = res_a.json()
    assert len(list_a) == 1
    assert list_a[0]["user_id"] == user_a.id

    res_b = client.get("/customers/", headers=headers_b)
    assert res_b.status_code == 200
    list_b = res_b.json()
    assert len(list_b) == 1
    assert list_b[0]["user_id"] == user_b.id

    res_admin = client.get("/customers/", headers=admin_headers)
    assert res_admin.status_code == 200
    list_admin = res_admin.json()
    assert len(list_admin) == 2


def test_customer_isolation_read(client, headers_a, user_b):
    customer_b_id = user_b.customer.customer_id
    response = client.get(f"/customers/{customer_b_id}", headers=headers_a)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_customer_isolation_update(client, headers_a, user_b):
    customer_b_id = user_b.customer.customer_id
    response = client.put(
        f"/customers/{customer_b_id}",
        json={"full_name": "Hacked Name"},
        headers=headers_a
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_customer_isolation_delete(client, headers_a, user_b):
    customer_b_id = user_b.customer.customer_id
    response = client.delete(f"/customers/{customer_b_id}", headers=headers_a)
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_customer_own_update(client, headers_a, user_a):
    customer_a_id = user_a.customer.customer_id
    response = client.put(
        f"/customers/{customer_a_id}",
        json={"address": "Updated Suite 404"},
        headers=headers_a
    )
    assert response.status_code == 200
    assert response.json()["address"] == "Updated Suite 404"


def test_admin_can_access_any_customer(client, admin_headers, user_a):
    customer_a_id = user_a.customer.customer_id
    response = client.get(f"/customers/{customer_a_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["customer_id"] == customer_a_id
