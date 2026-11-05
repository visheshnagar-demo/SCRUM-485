from fastapi.testclient import TestClient


def test_list_seeded_currencies(client: TestClient):
    response = client.get("/api/v1/currencies")
    assert response.status_code == 200
    currencies = response.json()
    assert len(currencies) >= 5
    codes = [c["code"] for c in currencies]
    assert "USD" in codes
    assert "EUR" in codes
    assert "GBP" in codes
    assert "JPY" in codes
    assert "CAD" in codes

    # Primary Base Currency should be USD
    usd = next(c for c in currencies if c["code"] == "USD")
    assert usd["is_base"] is True
    assert usd["symbol"] == "$"
    assert usd["is_active"] is True


def test_create_currency_valid_iso(client: TestClient):
    payload = {"code": "AUD", "symbol": "A$", "is_base": False, "is_active": True}
    response = client.post("/api/v1/currencies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "AUD"
    assert data["symbol"] == "A$"
    assert data["is_base"] is False
    assert data["is_active"] is True


def test_create_currency_invalid_iso_returns_422(client: TestClient):
    # Test four-letter invalid code "USDD"
    res1 = client.post("/api/v1/currencies", json={"code": "USDD", "symbol": "$"})
    assert res1.status_code == 422
    assert "Invalid ISO 4217 currency code" in res1.text

    # Test numeric invalid code "123"
    res2 = client.post("/api/v1/currencies", json={"code": "123", "symbol": "$"})
    assert res2.status_code == 422
    assert "Invalid ISO 4217 currency code" in res2.text

    # Test unknown three-letter code "XYZ"
    res3 = client.post("/api/v1/currencies", json={"code": "XYZ", "symbol": "$"})
    assert res3.status_code == 422
    assert "Invalid ISO 4217 currency code" in res3.text


def test_deactivate_base_currency_blocked(client: TestClient):
    # Attempting to deactivate USD (the base currency) must be blocked
    response = client.put("/api/v1/currencies/USD", json={"is_active": False})
    assert response.status_code in (400, 422)
    assert "Cannot deactivate the Primary Base Currency" in response.json()["detail"]


def test_delete_base_currency_blocked(client: TestClient):
    # Attempting to delete USD (the base currency) must be blocked
    response = client.delete("/api/v1/currencies/USD")
    assert response.status_code in (400, 422)
    assert "Cannot delete the Primary Base Currency" in response.json()["detail"]


def test_switch_primary_base_currency(client: TestClient):
    # Make EUR the new base currency
    response = client.put("/api/v1/currencies/EUR", json={"is_base": True})
    assert response.status_code == 200
    assert response.json()["is_base"] is True

    # Check that USD is no longer base
    usd_res = client.get("/api/v1/currencies/USD")
    assert usd_res.status_code == 200
    assert usd_res.json()["is_base"] is False

    # Switch back to USD as base
    reset_res = client.put("/api/v1/currencies/USD", json={"is_base": True})
    assert reset_res.status_code == 200
    assert reset_res.json()["is_base"] is True
