def test_reports_isolation(client, headers_a, headers_b, admin_headers, service_center):
    client.post(
        "/vehicles/",
        json={
            "registration_no": "REP-A-01",
            "brand": "Tesla",
            "model": "Model Y",
            "vehicle_type": "Electric"
        },
        headers=headers_a
    )
    client.post(
        "/vehicles/",
        json={
            "registration_no": "REP-B-01",
            "brand": "Volvo",
            "model": "XC90",
            "vehicle_type": "SUV"
        },
        headers=headers_b
    )

    types_a = client.get("/reports/vehicles-by-type", headers=headers_a).json()
    assert len(types_a) == 1
    assert types_a[0]["vehicle_type"] == "Electric"

    types_b = client.get("/reports/vehicles-by-type", headers=headers_b).json()
    assert len(types_b) == 1
    assert types_b[0]["vehicle_type"] == "SUV"

    types_admin = client.get("/reports/vehicles-by-type", headers=admin_headers).json()
    assert len(types_admin) == 2


def test_vehicle_service_history_security(client, headers_a, headers_b, service_center):
    v_res = client.post(
        "/vehicles/",
        json={
            "registration_no": "HIST-01",
            "brand": "Mercedes",
            "model": "C300",
            "vehicle_type": "Sedan"
        },
        headers=headers_a
    )
    v_id = v_res.json()["vehicle_id"]

    client.post(
        "/service-records/",
        json={
            "vehicle_id": v_id,
            "service_center_id": service_center.service_center_id,
            "service_date": "2026-07-01",
            "service_type": "Inspection",
            "service_cost": 80.00
        },
        headers=headers_a
    )

    forbidden_history = client.get(
        f"/reports/vehicle-service-history/{v_id}",
        headers=headers_b
    )
    assert forbidden_history.status_code == 403

    owner_history = client.get(
        f"/reports/vehicle-service-history/{v_id}",
        headers=headers_a
    )
    assert owner_history.status_code == 200
    assert len(owner_history.json()) == 1
