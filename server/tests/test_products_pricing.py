from decimal import Decimal
from fastapi.testclient import TestClient


def test_get_seeded_product_with_prices(client: TestClient):
    # Check prod-8832 ("Wireless Headphones")
    response = client.get("/api/v1/products/prod-8832")
    assert response.status_code == 200
    prod = response.json()
    assert prod["name"] == "Wireless Headphones"
    assert Decimal(str(prod["base_price"])) == Decimal("149.99")
    assert prod["base_currency_code"] == "USD"

    # Check explicit prices
    prices_res = client.get("/api/v1/products/prod-8832/prices")
    assert prices_res.status_code == 200
    prices = prices_res.json()
    curr_map = {p["currency_code"]: Decimal(str(p["price"])) for p in prices}
    assert curr_map.get("USD") == Decimal("149.99")
    assert curr_map.get("EUR") == Decimal("139.99")
    assert curr_map.get("GBP") == Decimal("119.99")


def test_configure_explicit_product_price(client: TestClient):
    # Configure an explicit CAD price for prod-8832
    payload = {"currency_code": "CAD", "price": 204.99, "is_active": True}
    response = client.post("/api/v1/products/prod-8832/prices", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["currency_code"] == "CAD"
    assert Decimal(str(data["price"])) == Decimal("204.99")
    assert data["is_active"] is True

    # Retrieve and verify explicit price is returned
    price_res = client.get("/api/v1/products/prod-8832/price?currency_code=CAD")
    assert price_res.status_code == 200
    price_data = price_res.json()
    assert price_data["is_explicit"] is True
    assert price_data["is_converted"] is False
    assert Decimal(str(price_data["price"])) == Decimal("204.99")
    assert price_data["symbol"] == "C$"


def test_negative_price_rejected_with_422(client: TestClient):
    # Submitting a negative price (-10.00) must return 422 validation error
    payload = {"currency_code": "EUR", "price": -10.00, "is_active": True}
    response = client.post("/api/v1/products/prod-8832/prices", json=payload)
    assert response.status_code == 422
    assert (
        "Price must be a positive decimal value greater than or equal to 0.00"
        in response.text
    )


def test_idempotent_price_update(client: TestClient):
    # Setting price for existing (product_id, currency_code) should update existing row
    payload1 = {"currency_code": "EUR", "price": 135.50, "is_active": True}
    res1 = client.post("/api/v1/products/prod-8832/prices", json=payload1)
    assert res1.status_code in (200, 201)

    prices_res = client.get("/api/v1/products/prod-8832/prices")
    eur_prices = [p for p in prices_res.json() if p["currency_code"] == "EUR"]
    assert len(eur_prices) == 1
    assert Decimal(str(eur_prices[0]["price"])) == Decimal("135.50")


def test_delete_product_price(client: TestClient):
    # Delete the CAD price we added
    del_res = client.delete("/api/v1/products/prod-8832/prices/CAD")
    assert del_res.status_code == 204

    # Verify CAD explicit price is deleted
    prices_res = client.get("/api/v1/products/prod-8832/prices")
    cad_prices = [p for p in prices_res.json() if p["currency_code"] == "CAD"]
    assert len(cad_prices) == 0
