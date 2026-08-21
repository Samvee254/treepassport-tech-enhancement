def test_register_and_login(client):
    res = client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "secretpass",
        "role": "field_officer",
    })
    assert res.status_code == 201
    assert res.json()["email"] == "alice@example.com"

    res = client.post("/auth/login", json={
        "email": "alice@example.com",
        "password": "secretpass",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password_fails(client):
    client.post("/auth/register", json={
        "name": "Bob",
        "email": "bob@example.com",
        "password": "correctpass",
        "role": "field_officer",
    })
    res = client.post("/auth/login", json={
        "email": "bob@example.com",
        "password": "wrongpass",
    })
    assert res.status_code == 401


def test_duplicate_email_rejected(client):
    payload = {
        "name": "Carol",
        "email": "carol@example.com",
        "password": "pass123",
        "role": "viewer",
    }
    res1 = client.post("/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/auth/register", json=payload)
    assert res2.status_code == 400
