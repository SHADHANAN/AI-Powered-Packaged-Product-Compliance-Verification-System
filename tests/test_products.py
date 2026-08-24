from fastapi.testclient import TestClient


def test_create_product(client: TestClient):
    """Test successful product creation via POST /api/products."""
    payload = {
        "product_name": "Premium Basmati Rice",
        "brand_name": "RoyalHarvest",
        "manufacturer_name": "Royal Mills Ltd, Punjab",
        "country_of_origin": "India",
        "net_quantity": "5",
        "unit": "kg",
        "batch_number": "BN-2025-88",
        "date_of_manufacture": "02/2025",
        "mrp": 450.0,
        "customer_care_details": "care@royalharvest.com, 1800-000-111",
    }
    response = client.post("/api/products", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["product_name"] == "Premium Basmati Rice"
    assert data["brand_name"] == "RoyalHarvest"
    assert data["mrp"] == 450.0
    assert "created_at" in data
    assert "updated_at" in data


def test_create_product_validation_error(client: TestClient):
    """Test validation error when mandatory product_name is missing or empty."""
    # Missing product_name
    response = client.post("/api/products", json={"brand_name": "BrandWithoutName"})
    assert response.status_code == 422
    assert "error" in response.json()

    # Empty product_name
    response_empty = client.post("/api/products", json={"product_name": ""})
    assert response_empty.status_code == 422


def test_get_product_by_id(client: TestClient):
    """Test retrieving an existing product by ID."""
    create_res = client.post("/api/products", json={"product_name": "Dark Chocolate 70%"})
    product_id = create_res.json()["id"]

    get_res = client.get(f"/api/products/{product_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == product_id
    assert get_res.json()["product_name"] == "Dark Chocolate 70%"


def test_get_product_not_found(client: TestClient):
    """Test proper 404 response for non-existent product ID."""
    response = client.get("/api/products/999999")
    assert response.status_code == 404
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == 404
    assert "not found" in body["error"]["message"].lower()


def test_list_products(client: TestClient):
    """Test listing products with pagination."""
    client.post("/api/products", json={"product_name": "Product 1"})
    client.post("/api/products", json={"product_name": "Product 2"})
    client.post("/api/products", json={"product_name": "Product 3"})

    list_res = client.get("/api/products?skip=0&limit=2")
    assert list_res.status_code == 200
    items = list_res.json()
    assert isinstance(items, list)
    assert len(items) == 2
