def test_list_products_default_currency(client):
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["selected_currency"] == "USD"
    assert data["total"] >= 6

    # Verify Wireless Headphones
    headphones = next((p for p in data["items"] if p["id"] == "prod-8832"), None)
    assert headphones is not None
    assert headphones["name"] == "Wireless Headphones"
    assert headphones["localized_price"]["price"] == 149.99
    assert headphones["localized_price"]["currency_code"] == "USD"
    assert headphones["localized_price"]["symbol"] == "$"


def test_list_products_filter_and_search(client):
    # Filter by category Audio
    response = client.get("/api/v1/products?category=Audio")
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert "Audio" in item["category"]

    # Search by keyword
    response2 = client.get("/api/v1/products?search=Smartwatch")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["total"] == 1
    assert data2["items"][0]["name"] == "Smartwatch"


def test_create_and_get_product(client):
    new_product_payload = {
        "id": "prod-test-99",
        "name": "Noise Cancelling Earbuds",
        "description": "High fidelity sound with multi-mic array",
        "category": "Audio",
        "sku": "NCE-99",
        "rating": 4.5,
        "reviews_count": 50,
        "in_stock": True,
        "base_price": 89.99,
    }
    create_res = client.post("/api/v1/products", json=new_product_payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["id"] == "prod-test-99"
    assert created["name"] == "Noise Cancelling Earbuds"
    assert created["localized_price"]["price"] == 89.99

    # Get product by ID
    get_res = client.get("/api/v1/products/prod-test-99")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Noise Cancelling Earbuds"


def test_update_and_delete_product(client):
    # Create test product first
    new_product_payload = {
        "id": "prod-test-update-delete",
        "name": "Noise Cancelling Earbuds",
        "description": "High fidelity sound with multi-mic array",
        "category": "Audio",
        "sku": "NCE-UD",
        "rating": 4.5,
        "reviews_count": 50,
        "in_stock": True,
        "base_price": 89.99,
    }
    create_res = client.post("/api/v1/products", json=new_product_payload)
    assert create_res.status_code == 201

    update_res = client.put(
        "/api/v1/products/prod-test-update-delete",
        json={"name": "Noise Cancelling Earbuds Ultra", "rating": 4.8},
    )
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Noise Cancelling Earbuds Ultra"
    assert update_res.json()["rating"] == 4.8

    del_res = client.delete("/api/v1/products/prod-test-update-delete")
    assert del_res.status_code == 204

    get_res = client.get("/api/v1/products/prod-test-update-delete")
    assert get_res.status_code == 404
