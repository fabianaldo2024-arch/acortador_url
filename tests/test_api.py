"""
Integration tests for the Shortener API Endpoints.
Pruebas de integración para los Endpoints de la API del acortador.
"""

import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_healthcheck_endpoint(client: AsyncClient) -> None:
    """Verify healthcheck endpoint / Verifica endpoint /health."""
    response = await client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "healthy"
    assert json_data["database"] == "connected"

@pytest.mark.asyncio
async def test_create_short_url(client: AsyncClient) -> None:
    """Verify URL creation / Verifica creación de URL acortada."""
    payload = {"target_url": "https://python.org"}
    response = await client.post("/api/v1/shorten", json=payload)
    
    assert response.status_code in (200, 201)
    data = response.json()
    assert "short_code" in data
    assert data["target_url"].rstrip("/") == "https://python.org"

@pytest.mark.asyncio
async def test_redirect_non_existent_url(client: AsyncClient) -> None:
    """Verify 404 on missing short code / Verifica 404 para código inexistente."""
    response = await client.get("/invalid_code_123")
    assert response.status_code == 404
