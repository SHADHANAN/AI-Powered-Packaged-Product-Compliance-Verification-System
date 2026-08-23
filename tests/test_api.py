from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test health check endpoint GET /api/health."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "packaged-product-compliance-backend",
    }


def test_openapi_docs(client: TestClient):
    """Test that OpenAPI docs are served at /docs and schema at /openapi.json."""
    docs_res = client.get("/docs")
    assert docs_res.status_code == 200

    openapi_res = client.get("/openapi.json")
    assert openapi_res.status_code == 200
    schema = openapi_res.json()
    assert "/api/health" in schema["paths"]
    assert "/api/products" in schema["paths"]
    assert "/api/verifications/{verification_id}" in schema["paths"]
    assert "/api/ocr" in schema["paths"]
    assert "/api/extract" in schema["paths"]
    assert "/api/compliance/evaluate" in schema["paths"]
    assert "/api/explanation" in schema["paths"]
    assert "/api/verify" in schema["paths"]


def test_cors_headers(client: TestClient):
    """Test CORS preflight response headers."""
    response = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
