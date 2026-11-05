from decimal import Decimal
from fastapi.testclient import TestClient


def test_dynamic_exchange_rate_conversion(client: TestClient):
    # Create a test product with $100.00 USD base price and no explicit CAD price
    prod_payload = {
        "id": "prod-test-conversion",
        "name": "Standard Test Item",
        "description": "Used to test dynamic exchange rate conversion",
        "category": "Testing",
        "base_price": 100.00,
        "base_currency_code": "USD",
        "is_active": True,
    }
    client.post("/api/v1/products", json=prod_payload)

    # Ensure exchange rate 1 USD = 1.35 CAD exists
    rate_payload = {
        "from_currency_code": "USD",
        "to_currency_code": "CAD",
        "rate": 1.350000,
        "is_active": True,
    }
    client.post("/api/v1/exchange-rates", json=rate_payload)

    # Request price in CAD
    price_res = client.get(
        "/api/v1/products/prod-test-conversion/price?currency_code=CAD"
    )
    assert price_res.status_code == 200
    price_data = price_res.json()
    assert price_data["is_explicit"] is False
    assert price_data["is_converted"] is True
    assert price_data["is_fallback"] is False
    assert Decimal(str(price_data["price"])) == Decimal("135.00")
    assert price_data["currency_code"] == "CAD"
    assert price_data["symbol"] == "C$"
    assert "135.00" in price_data["formatted_price"]


def test_fallback_to_base_currency_when_no_rate_exists(client: TestClient):
    # Create an enabled currency with no exchange rate, e.g. "CHF"
    curr_payload = {"code": "CHF", "symbol": "CHF", "is_base": False, "is_active": True}
    client.post("/api/v1/currencies", json=curr_payload)

    # Request price in CHF for prod-test-conversion
    price_res = client.get(
        "/api/v1/products/prod-test-conversion/price?currency_code=CHF"
    )
    assert price_res.status_code == 200
    price_data = price_res.json()
    # Should fallback to USD base price
    assert price_data["is_fallback"] is True
    assert price_data["is_converted"] is False
    assert price_data["currency_code"] == "USD"
    assert price_data["symbol"] == "$"
    assert Decimal(str(price_data["price"])) == Decimal("100.00")


def test_product_listing_with_currency_query_param(client: TestClient):
    # List products with currency=CAD
    response = client.get("/api/v1/products?currency=CAD")
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    for item in items:
        loc = item["localized_price"]
        assert loc is not None
        assert loc["currency_code"] in ("CAD", "USD")
