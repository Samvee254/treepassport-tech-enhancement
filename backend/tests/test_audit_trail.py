def test_sensitive_field_change_is_flagged(client, field_officer_token):
    headers = {"Authorization": f"Bearer {field_officer_token}"}
    res = client.post(
        "/trees",
        json={"tree_code": "TP-AUDIT-001", "gps_lat": -1.5, "gps_lng": 37.0},
        headers=headers,
    )
    tree_id = res.json()["id"]

    client.patch(
        f"/trees/{tree_id}",
        json={"gps_lat": -1.29},
        headers=headers,
    )

    res = client.get(f"/trees/{tree_id}/audit", headers=headers)
    logs = res.json()
    assert len(logs) == 1
    assert logs[0]["field_changed"] == "gps_lat"
    assert logs[0]["flagged"] is True
    assert logs[0]["old_value"] == "-1.5"
    assert logs[0]["new_value"] == "-1.29"


def test_monitoring_create_logs_but_does_not_flag(client, field_officer_token):
    headers = {"Authorization": f"Bearer {field_officer_token}"}
    res = client.post(
        "/trees", json={"tree_code": "TP-AUDIT-002"}, headers=headers
    )
    tree_id = res.json()["id"]

    client.post(
        f"/trees/{tree_id}/monitoring",
        json={"height_cm": 20, "health_status": "healthy"},
        headers=headers,
    )

    res = client.get(f"/trees/{tree_id}/audit", headers=headers)
    logs = res.json()
    assert len(logs) == 1
    assert logs[0]["field_changed"] == "monitoring_record_added"
    assert logs[0]["flagged"] is False


def test_viewer_cannot_see_audit_log(client, field_officer_token, viewer_token):
    res = client.post(
        "/trees",
        json={"tree_code": "TP-AUDIT-003"},
        headers={"Authorization": f"Bearer {field_officer_token}"},
    )
    tree_id = res.json()["id"]

    res = client.get(
        f"/trees/{tree_id}/audit",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert res.status_code == 403
