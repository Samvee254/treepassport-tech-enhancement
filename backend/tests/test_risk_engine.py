def _create_tree(client, token):
    res = client.post(
        "/trees",
        json={"tree_code": "TP-RISK-001", "county": "TestCounty"},
        headers={"Authorization": f"Bearer {token}"},
    )
    return res.json()["id"]


def test_tree_with_no_monitoring_is_high_risk(client, field_officer_token):
    tree_id = _create_tree(client, field_officer_token)
    res = client.get(f"/trees/{tree_id}/risk")
    assert res.status_code == 200
    data = res.json()
    assert data["bucket"] == "HIGH"
    assert data["score"] == 100


def test_healthy_recent_checkin_is_low_risk(client, field_officer_token):
    tree_id = _create_tree(client, field_officer_token)
    headers = {"Authorization": f"Bearer {field_officer_token}"}
    client.post(
        f"/trees/{tree_id}/monitoring",
        json={"height_cm": 30, "health_status": "healthy"},
        headers=headers,
    )
    res = client.get(f"/trees/{tree_id}/risk")
    data = res.json()
    assert data["bucket"] == "LOW"
    assert data["score"] <= 20


def test_health_decline_forces_at_least_medium(client, field_officer_token):
    tree_id = _create_tree(client, field_officer_token)
    headers = {"Authorization": f"Bearer {field_officer_token}"}
    client.post(
        f"/trees/{tree_id}/monitoring",
        json={"height_cm": 30, "health_status": "healthy"},
        headers=headers,
    )
    client.post(
        f"/trees/{tree_id}/monitoring",
        json={"height_cm": 32, "health_status": "moderate"},
        headers=headers,
    )
    res = client.get(f"/trees/{tree_id}/risk")
    data = res.json()
    # regression test for the bucket-masking bug found during manual testing
    assert data["bucket"] in ("MEDIUM", "HIGH")
    assert data["breakdown"]["health_status"]["declined_since_previous"] is True


def test_missing_checkins_calculated_correctly(client, field_officer_token):
    headers = {"Authorization": f"Bearer {field_officer_token}"}
    res = client.post(
        "/trees",
        json={
            "tree_code": "TP-RISK-W4-001",
            "planting_date": "2026-01-01T00:00:00",
        },
        headers=headers,
    )
    tree_id = res.json()["id"]
    client.post(
        f"/trees/{tree_id}/monitoring",
        json={"height_cm": 20, "health_status": "healthy"},
        headers=headers,
    )

    res = client.get(f"/trees/{tree_id}/risk")
    data = res.json()
    mc = data["breakdown"]["missing_checkins"]
    assert mc["actual_checkins"] == 1
    assert mc["expected_checkins"] > mc["actual_checkins"]
    assert mc["missing"] > 0


def test_overdue_monitoring_forces_at_least_medium(client, field_officer_token):
    headers = {"Authorization": f"Bearer {field_officer_token}"}
    res = client.post(
        "/trees",
        json={
            "tree_code": "TP-RISK-W4-002",
            "planting_date": "2026-01-01T00:00:00",
        },
        headers=headers,
    )
    tree_id = res.json()["id"]
    client.post(
        f"/trees/{tree_id}/monitoring",
        json={"height_cm": 20, "health_status": "healthy"},
        headers=headers,
    )

    res = client.get(f"/trees/{tree_id}/risk")
    data = res.json()
    # regression test for the overdue-monitoring bucket-masking bug
    assert data["breakdown"]["missing_checkins"]["missing"] >= 3
    assert data["bucket"] in ("MEDIUM", "HIGH")
