def test_list_currencies(client):
    response = client.get("/api/v1/currencies")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 5
    codes = [c["code"] for c in data["items"]]
    assert "USD" in codes
    assert "EUR" in codes
    assert "GBP" in codes
    assert "JPY" in codes
    assert "CAD" in codes


def test_get_base_currency(client):
    response = client.get("/api/v1/currencies/base")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "USD"
    assert data["is_base"] is True
    assert data["is_active"] is True


def test_create_currency_success(client):
    payload = {
        "code": "AUD",
        "name": "Australian Dollar",
        "symbol": "A$",
        "is_base": False,
        "is_active": True,
    }
    response = client.post("/api/v1/currencies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "AUD"
    assert data["symbol"] == "A$"
    assert data["is_base"] is False


def test_create_currency_invalid_iso_code(client):
    # Invalid length (4 chars)
    response = client.post(
        "/api/v1/currencies",
        json={"code": "USDD", "symbol": "$", "name": "Invalid USD"},
    )
    assert response.status_code == 422

    # Numeric code
    response2 = client.post(
        "/api/v1/currencies",
        json={"code": "123", "symbol": "$", "name": "Numeric Code"},
    )
    assert response2.status_code == 422


def test_create_duplicate_currency_conflict(client):
    response = client.post(
        "/api/v1/currencies",
        json={"code": "EUR", "symbol": "€", "name": "Duplicate Euro"},
    )
    assert response.status_code == 409


def test_designate_new_base_currency(client):
    # Update EUR to be base currency
    response = client.put("/api/v1/currencies/EUR", json={"is_base": True})
    assert response.status_code == 200
    eur_data = response.json()
    assert eur_data["is_base"] is True

    # Check USD is no longer base
    usd_res = client.get("/api/v1/currencies/USD")
    assert usd_res.status_code == 200
    assert usd_res.json()["is_base"] is False

    # Restore USD as base currency
    client.put("/api/v1/currencies/USD", json={"is_base": True})


def test_deactivate_base_currency_blocked(client):
    # Try to deactivate USD while it is the base currency
    response = client.put("/api/v1/currencies/USD", json={"is_active": False})
    assert response.status_code == 422
    assert "Cannot deactivate primary base currency" in response.json()["detail"]


def test_delete_base_currency_blocked(client):
    response = client.delete("/api/v1/currencies/USD")
    assert response.status_code == 400
    assert "Cannot delete the primary base currency" in response.json()["detail"]


def test_delete_non_base_currency(client):
    # Create temp currency
    create_res = client.post(
        "/api/v1/currencies",
        json={"code": "CHF", "symbol": "CHF", "name": "Swiss Franc", "is_base": False},
    )
    assert create_res.status_code == 201

    # Delete temp currency
    del_res = client.delete("/api/v1/currencies/CHF")
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get("/api/v1/currencies/CHF")
    assert get_res.status_code == 404
