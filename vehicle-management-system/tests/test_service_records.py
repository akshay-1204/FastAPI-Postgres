def test_service_record_ownership(client, headers_a, headers_b, admin_headers, service_center):
    vehicle_res = client.post(
        "/vehicles/",
        json={
            "registration_no": "SRV-TEST-01",
            "brand": "BMW",
            "model": "330i",
            "vehicle_type": "Sedan"
        },
        headers=headers_a
    )
    assert vehicle_res.status_code == 201
    v_id = vehicle_res.json()["vehicle_id"]
    c_id = service_center.service_center_id

    unauthorized_create = client.post(
        "/service-records/",
        json={
            "vehicle_id": v_id,
            "service_center_id": c_id,
            "service_date": "2026-05-15",
            "service_type": "Oil Change",
            "service_cost": 120.00
        },
        headers=headers_b
    )
    assert unauthorized_create.status_code == 403

    authorized_create = client.post(
        "/service-records/",
        json={
            "vehicle_id": v_id,
            "service_center_id": c_id,
            "service_date": "2026-05-15",
            "service_type": "Oil Change",
            "service_cost": 120.00
        },
        headers=headers_a
    )
    assert authorized_create.status_code == 201
    srv_id = authorized_create.json()["service_id"]

    unauthorized_read = client.get(f"/service-records/{srv_id}", headers=headers_b)
    assert unauthorized_read.status_code == 403

    authorized_read = client.get(f"/service-records/{srv_id}", headers=headers_a)
    assert authorized_read.status_code == 200
    assert authorized_read.json()["service_type"] == "Oil Change"

    admin_read = client.get(f"/service-records/{srv_id}", headers=admin_headers)
    assert admin_read.status_code == 200
