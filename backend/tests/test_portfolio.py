def test_portfolio_lifecycle(client):
    # Register user
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "portfolio_mgr@mats.ai",
        "password": "ManagerPass123!",
        "full_name": "Portfolio Manager"
    })
    assert reg_res.status_code == 201
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Verify initial default portfolio was seeded
    get_res = client.get("/api/v1/portfolio/", headers=headers)
    assert get_res.status_code == 200
    portfolios = get_res.json()
    assert len(portfolios) >= 1
    default_p = portfolios[0]
    assert "Portfolio" in default_p["name"]

    # Create new secondary portfolio
    new_p_res = client.post("/api/v1/portfolio/", headers=headers, json={
        "name": "Crypto Macro Hedge",
        "description": "Digital assets exposure",
        "cash_balance": 15000.0,
        "currency": "USD"
    })
    assert new_p_res.status_code == 201
    p_id = new_p_res.json()["id"]

    # Add holding
    holding_res = client.post(f"/api/v1/portfolio/{p_id}/holdings", headers=headers, json={
        "symbol": "BTC",
        "asset_type": "Crypto",
        "quantity": 1.5,
        "buy_price": 64000.0,
        "current_value": 98000.0
    })
    assert holding_res.status_code == 201
    assert holding_res.json()["symbol"] == "BTC"


def test_watchlist_and_profile(client):
    login_res = client.post("/api/v1/auth/login", json={
        "email": "portfolio_mgr@mats.ai",
        "password": "ManagerPass123!"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Check watchlist
    wl_res = client.get("/api/v1/watchlist/", headers=headers)
    assert wl_res.status_code == 200
    watchlists = wl_res.json()
    assert len(watchlists) >= 1
    assert "NVDA" in watchlists[0]["symbols"]

    # Check and update profile
    profile_res = client.get("/api/v1/profile/", headers=headers)
    assert profile_res.status_code == 200
    assert profile_res.json()["risk_tolerance"] == "moderate"

    update_res = client.put("/api/v1/profile/", headers=headers, json={
        "risk_tolerance": "aggressive",
        "target_return": 25.0
    })
    assert update_res.status_code == 200
    assert update_res.json()["risk_tolerance"] == "aggressive"
