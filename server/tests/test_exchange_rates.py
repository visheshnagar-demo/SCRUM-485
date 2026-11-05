def test_list_exchange_rates(client):
    response = client.get("/api/v1/exchange-rates")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 4

    pairs = [(r["from_currency"], r["to_currency"]) for r in data["items"]]
    assert ("USD", "EUR") in pairs
    assert ("USD", "GBP") in pairs
    assert ("USD", "CAD") in pairs


def test_create_and_get_exchange_rate(client):
    payload = {
        "from_currency": "EUR",
        "to_currency": "GBP",
        "rate": 0.865,
        "is_active": True,
    }
    create_res = client.post("/api/v1/exchange-rates", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["from_currency"] == "EUR"
    assert created["to_currency"] == "GBP"
    assert created["rate"] == 0.865

    rate_id = created["id"]
    get_res = client.get(f"/api/v1/exchange-rates/{rate_id}")
    assert get_res.status_code == 200
    assert get_res.json()["rate"] == 0.865


def test_create_invalid_exchange_rate_rejected(client):
    # Negative rate
    response = client.post(
        "/api/v1/exchange-rates",
        json={"from_currency": "EUR", "to_currency": "USD", "rate": -1.25},
    )
    assert response.status_code == 422

    # Zero rate
    response2 = client.post(
        "/api/v1/exchange-rates",
        json={"from_currency": "EUR", "to_currency": "USD", "rate": 0.0},
    )
    assert response2.status_code == 422


def test_update_and_delete_exchange_rate(client):
    # Create rate first for self-contained test
    create_res = client.post(
        "/api/v1/exchange-rates",
        json={"from_currency": "EUR", "to_currency": "GBP", "rate": 0.865},
    )
    assert create_res.status_code == 201
    rate_id = create_res.json()["id"]

    update_res = client.put(
        f"/api/v1/exchange-rates/{rate_id}",
        json={"rate": 0.875},
    )
    assert update_res.status_code == 200
    assert update_res.json()["rate"] == 0.875

    del_res = client.delete(f"/api/v1/exchange-rates/{rate_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/exchange-rates/{rate_id}")
    assert get_res.status_code == 404
