def test_parts_flow_and_ownership(client, headers_a, headers_b, service_center):
    v_res = client.post(
        "/vehicles/",
        json={
            "registration_no": "PART-V-01",
            "brand": "Audi",
            "model": "A4",
            "vehicle_type": "Sedan"
        },
        headers=headers_a
    )
    v_id = v_res.json()["vehicle_id"]
    c_id = service_center.service_center_id

    srv_res = client.post(
        "/service-records/",
        json={
            "vehicle_id": v_id,
            "service_center_id": c_id,
            "service_date": "2026-06-01",
            "service_type": "Brake Replacement"
        },
        headers=headers_a
    )
    srv_id = srv_res.json()["service_id"]

    unauthorized_part = client.post(
        "/vehicle-parts/",
        json={
            "service_id": srv_id,
            "part_name": "Brake Rotor",
            "quantity": 2,
            "unit_price": 85.00
        },
        headers=headers_b
    )
    assert unauthorized_part.status_code == 403

    authorized_part = client.post(
        "/vehicle-parts/",
        json={
            "service_id": srv_id,
            "part_name": "Brake Rotor",
            "part_number": "BRK-8821",
            "quantity": 2,
            "unit_price": 85.00,
            "warranty_months": 12
        },
        headers=headers_a
    )
    assert authorized_part.status_code == 201
    part_id = authorized_part.json()["part_id"]
    assert float(authorized_part.json()["total_price"]) == 170.00

    unauthorized_read = client.get(f"/vehicle-parts/{part_id}", headers=headers_b)
    assert unauthorized_read.status_code == 403

    authorized_read = client.get(f"/vehicle-parts/{part_id}", headers=headers_a)
    assert authorized_read.status_code == 200
    assert authorized_read.json()["part_name"] == "Brake Rotor"
