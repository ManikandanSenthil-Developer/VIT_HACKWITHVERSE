def test_user_registration_and_jwt(client):
    res = client.post("/api/v1/auth/register", json={
        "email": "trader@mats.ai",
        "password": "SecureTraderPass123!",
        "full_name": "Autonomous Market Trader"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "trader@mats.ai"


def test_login_invalid_credentials(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "trader@mats.ai",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401


def test_get_current_user_me(client):
    # Login to get fresh token
    login_res = client.post("/api/v1/auth/login", json={
        "email": "trader@mats.ai",
        "password": "SecureTraderPass123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "trader@mats.ai"


def test_refresh_token(client):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "trader@mats.ai",
        "password": "SecureTraderPass123!"
    })
    refresh_token = login_res.json()["refresh_token"]
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 200
    assert "access_token" in res.json()
