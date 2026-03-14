import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_docs_endpoint_accessible(client: AsyncClient):
    """Test that the OpenAPI docs endpoint is accessible."""
    response = await client.get("/docs")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_openapi_json_accessible(client: AsyncClient):
    """Test that the OpenAPI JSON schema is accessible."""
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
