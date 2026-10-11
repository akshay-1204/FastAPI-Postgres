def test_service_center_permissions(client, headers_a, admin_headers, service_center):
    read_res = client.get("/service-centers/", headers=headers_a)
    assert read_res.status_code == 200
    assert len(read_res.json()) >= 1

    customer_create = client.post(
        "/service-centers/",
        json={"center_name": "Rogue Workshop"},
        headers=headers_a
    )
    assert customer_create.status_code == 403

    admin_create = client.post(
        "/service-centers/",
        json={
            "center_name": "Official Regional Garage",
            "city": "Capital City",
            "rating": 4.9
        },
        headers=admin_headers
    )
    assert admin_create.status_code == 201
    center_id = admin_create.json()["service_center_id"]

    customer_delete = client.delete(
        f"/service-centers/{center_id}",
        headers=headers_a
    )
    assert customer_delete.status_code == 403

    admin_delete = client.delete(
        f"/service-centers/{center_id}",
        headers=admin_headers
    )
    assert admin_delete.status_code == 200
