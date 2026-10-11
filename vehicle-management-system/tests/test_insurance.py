def test_insurance_flow_and_ownership(client, headers_a, headers_b):
    vehicle_res = client.post(
        "/vehicles/",
        json={
            "registration_no": "INS-TEST-01",
            "brand": "Hyundai",
            "model": "Creta",
            "vehicle_type": "SUV"
        },
        headers=headers_a
    )
    assert vehicle_res.status_code == 201
    v_id = vehicle_res.json()["vehicle_id"]

    foreign_attempt = client.post(
        "/insurance/",
        json={
            "vehicle_id": v_id,
            "policy_number": "POL-HACK-01",
            "insurance_company": "SecureLife",
            "start_date": "2026-01-01",
            "end_date": "2027-01-01",
            "premium_amount": 500.00,
            "status": "Active"
        },
        headers=headers_b
    )
    assert foreign_attempt.status_code == 403

    valid_policy = client.post(
        "/insurance/",
        json={
            "vehicle_id": v_id,
            "policy_number": "POL-ALICE-01",
            "insurance_company": "StateFarm",
            "start_date": "2026-01-01",
            "end_date": "2027-01-01",
            "premium_amount": 650.00,
            "status": "Active"
        },
        headers=headers_a
    )
    assert valid_policy.status_code == 201
    ins_id = valid_policy.json()["insurance_id"]

    dup_policy = client.post(
        "/insurance/",
        json={
            "vehicle_id": v_id,
            "policy_number": "POL-ALICE-01",
            "insurance_company": "Geico",
            "start_date": "2026-01-01",
            "end_date": "2027-01-01",
            "premium_amount": 600.00,
            "status": "Active"
        },
        headers=headers_a
    )
    assert dup_policy.status_code == 409

    forbidden_read = client.get(f"/insurance/{ins_id}", headers=headers_b)
    assert forbidden_read.status_code == 403

    owner_read = client.get(f"/insurance/{ins_id}", headers=headers_a)
    assert owner_read.status_code == 200
    assert owner_read.json()["policy_number"] == "POL-ALICE-01"


def test_insurance_invalid_dates(client, headers_a):
    vehicle_res = client.post(
        "/vehicles/",
        json={
            "registration_no": "DATE-TEST-01",
            "brand": "Nissan",
            "model": "Rogue",
            "vehicle_type": "SUV"
        },
        headers=headers_a
    )
    v_id = vehicle_res.json()["vehicle_id"]

    response = client.post(
        "/insurance/",
        json={
            "vehicle_id": v_id,
            "policy_number": "POL-INVALID-DATES",
            "insurance_company": "TestCo",
            "start_date": "2026-10-10",
            "end_date": "2026-01-01",
            "premium_amount": 100.00
        },
        headers=headers_a
    )
    assert response.status_code == 422
