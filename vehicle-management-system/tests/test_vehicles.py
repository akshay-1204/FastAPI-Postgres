def test_create_and_read_vehicle(client, headers_a, user_a):
    payload = {
        "registration_no": "KA-01-AB-1234",
        "brand": "Toyota",
        "model": "Camry",
        "vehicle_type": "Sedan",
        "manufacturing_year": 2022,
        "color": "Silver",
        "purchase_price": 28000.00
    }
    response = client.post("/vehicles/", json=payload, headers=headers_a)
    assert response.status_code == 201
    data = response.json()
    assert data["registration_no"] == "KA-01-AB-1234"
    assert data["customer_id"] == user_a.customer.customer_id


def test_duplicate_registration_rejected(client, headers_a):
    payload = {
        "registration_no": "KA-01-XX-9999",
        "brand": "Honda",
        "model": "Civic",
        "vehicle_type": "Sedan"
    }
    first_res = client.post("/vehicles/", json=payload, headers=headers_a)
    assert first_res.status_code == 201

    second_res = client.post("/vehicles/", json=payload, headers=headers_a)
    assert second_res.status_code == 409
    assert "already exists" in second_res.json()["detail"]


def test_vehicle_isolation(client, headers_a, headers_b, admin_headers):
    payload_a = {
        "registration_no": "ALICE-01",
        "brand": "Tesla",
        "model": "Model 3",
        "vehicle_type": "Electric"
    }
    res_a = client.post("/vehicles/", json=payload_a, headers=headers_a)
    assert res_a.status_code == 201
    vehicle_a_id = res_a.json()["vehicle_id"]

    payload_b = {
        "registration_no": "BOB-01",
        "brand": "Ford",
        "model": "F-150",
        "vehicle_type": "Truck"
    }
    res_b = client.post("/vehicles/", json=payload_b, headers=headers_b)
    assert res_b.status_code == 201
    vehicle_b_id = res_b.json()["vehicle_id"]

    list_a = client.get("/vehicles/", headers=headers_a).json()
    assert any(v["vehicle_id"] == vehicle_a_id for v in list_a)
    assert not any(v["vehicle_id"] == vehicle_b_id for v in list_a)

    list_b = client.get("/vehicles/", headers=headers_b).json()
    assert any(v["vehicle_id"] == vehicle_b_id for v in list_b)
    assert not any(v["vehicle_id"] == vehicle_a_id for v in list_b)

    list_admin = client.get("/vehicles/", headers=admin_headers).json()
    assert any(v["vehicle_id"] == vehicle_a_id for v in list_admin)
    assert any(v["vehicle_id"] == vehicle_b_id for v in list_admin)

    forbidden_read = client.get(f"/vehicles/{vehicle_a_id}", headers=headers_b)
    assert forbidden_read.status_code == 403

    forbidden_update = client.put(
        f"/vehicles/{vehicle_a_id}",
        json={"color": "Pink"},
        headers=headers_b
    )
    assert forbidden_update.status_code == 403

    forbidden_delete = client.delete(f"/vehicles/{vehicle_a_id}", headers=headers_b)
    assert forbidden_delete.status_code == 403
