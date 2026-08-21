def test_create_tree_requires_auth(client):
    res = client.post("/trees", json={"tree_code": "TP-TEST-001"})
    assert res.status_code == 401


def test_field_officer_can_create_tree(client, field_officer_token):
    res = client.post(
        "/trees",
        json={"tree_code": "TP-TEST-001", "county": "TestCounty"},
        headers={"Authorization": f"Bearer {field_officer_token}"},
    )
    assert res.status_code == 201
    assert res.json()["tree_code"] == "TP-TEST-001"
    assert res.json()["verification_status"] == "pending"


def test_viewer_cannot_create_tree(client, viewer_token):
    res = client.post(
        "/trees",
        json={"tree_code": "TP-TEST-002"},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res.status_code == 403


def test_viewer_can_read_trees(client, field_officer_token, viewer_token):
    client.post(
        "/trees",
        json={"tree_code": "TP-TEST-003"},
        headers={"Authorization": f"Bearer {field_officer_token}"},
    )
    res = client.get("/trees", headers={"Authorization": f"Bearer {viewer_token}"})
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_duplicate_tree_code_rejected(client, field_officer_token):
    headers = {"Authorization": f"Bearer {field_officer_token}"}
    client.post("/trees", json={"tree_code": "TP-DUP-001"}, headers=headers)
    res = client.post("/trees", json={"tree_code": "TP-DUP-001"}, headers=headers)
    assert res.status_code == 400
