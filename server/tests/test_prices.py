def test_get_product_prices(client):
    response = client.get("/api/v1/products/prod-8832/prices")
    assert response.status_code == 200
    prices = response.json()
    assert len(prices) >= 3
    currencies = [p["currency_code"] for p in prices]
    assert "USD" in currencies
    assert "EUR" in currencies
    assert "GBP" in currencies


def test_set_explicit_product_price_success(client):
    payload = {
        "currency_code": "JPY",
        "price": 22800.0,
        "is_active": True,
    }
    response = client.post("/api/v1/products/prod-8832/prices", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["currency_code"] == "JPY"
    assert data["price"] == 22800.0

    # Retrieve product with JPY
    prod_res = client.get("/api/v1/products/prod-8832?currency=JPY")
    assert prod_res.status_code == 200
    prod_data = prod_res.json()
    assert prod_data["localized_price"]["currency_code"] == "JPY"
    assert prod_data["localized_price"]["price"] == 22800.0
    assert prod_data["localized_price"]["is_converted"] is False


def test_negative_price_rejected_with_422(client):
    payload = {
        "currency_code": "EUR",
        "price": -10.00,
        "is_active": True,
    }
    response = client.post("/api/v1/products/prod-8832/prices", json=payload)
    assert response.status_code == 422


def test_exchange_rate_conversion_fallback(client):
    # Product prod-8833 (Smartwatch) has base price $249.99 USD and no explicit CAD price
    # Exchange rate USD -> CAD is 1.365
    response = client.get("/api/v1/products/prod-8833?currency=CAD")
    assert response.status_code == 200
    data = response.json()
    loc = data["localized_price"]
    assert loc["currency_code"] == "CAD"
    assert loc["is_converted"] is True
    assert loc["is_fallback"] is False
    # Expected: 249.99 * 1.365 = 341.2364
    assert abs(loc["price"] - (249.99 * 1.365)) < 0.01


def test_no_price_and_no_rate_fallback_to_base_currency(client):
    # Add currency without exchange rate: NZD
    curr_res = client.post(
        "/api/v1/currencies",
        json={
            "code": "NZD",
            "symbol": "NZ$",
            "name": "New Zealand Dollar",
            "is_base": False,
        },
    )
    assert curr_res.status_code == 201

    # Fetch product prod-8833 with NZD (no explicit price and no rate configured)
    response = client.get("/api/v1/products/prod-8833?currency=NZD")
    assert response.status_code == 200
    data = response.json()
    loc = data["localized_price"]
    # Fallback to base currency (USD)
    assert loc["currency_code"] == "USD"
    assert loc["is_fallback"] is True
    assert loc["price"] == 249.99


def test_update_and_delete_product_price(client):
    # Set explicit price first
    set_res = client.post(
        "/api/v1/products/prod-8832/prices",
        json={"currency_code": "JPY", "price": 22800.0, "is_active": True},
    )
    assert set_res.status_code == 201
    price_id = set_res.json()["id"]

    # Update JPY price
    up_res = client.put(
        f"/api/v1/products/prod-8832/prices/{price_id}",
        json={"price": 23000.0},
    )
    assert up_res.status_code == 200
    assert up_res.json()["price"] == 23000.0

    # Delete JPY price
    del_res = client.delete(f"/api/v1/products/prod-8832/prices/{price_id}")
    assert del_res.status_code == 204
