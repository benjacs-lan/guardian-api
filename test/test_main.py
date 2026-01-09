"""
Unit tests for main.py endpoints.

This module contains unit tests for the Guardian API endpoints using pytest and httpx.
"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.app.main import app
from src.app.redis_client import RedisClientManager
from unittest.mock import AsyncMock, patch


@pytest.fixture
def client():
    """TestClient síncrono de FastAPI."""
    return TestClient(app)


@pytest.fixture
async def async_client():
    """AsyncClient de httpx  para endpoints síncronos."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, async_client):
        """Test successful health check."""
        with patch.object(RedisClientManager, 'ping', new_callable=AsyncMock) as mock_ping:
            mock_ping.return_value = True

            response = await async_client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["redis"] == "connected"

    @pytest.mark.asyncio
    async def test_health_check_redis_failure(self, async_client):
        """Test health check with Redis failure."""
        with patch.object(RedisClientManager, 'ping', new_callable=AsyncMock) as mock_ping:
            mock_ping.side_effect = Exception("Connection failed")

            response = await async_client.get("/health")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert "unavailable" in data["redis"]


class TestDataEndpoints:
    """Tests for data store and retrieve endpoints."""

    @pytest.mark.asyncio
    async def test_store_data_success(self, async_client):
        """Test successful data storage."""
        with patch.object(RedisClientManager, 'set', new_callable=AsyncMock) as mock_set:
            data = {"key": "test_key", "value": "test_value"}

            response = await async_client.post("/data", json=data)

            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert result["data"] == data
            mock_set.assert_called_once_with("test_key", "test_value")

    @pytest.mark.asyncio
    async def test_store_data_failure(self, async_client):
        """Test data storage failure."""
        with patch.object(RedisClientManager, 'set', new_callable=AsyncMock) as mock_set:
            mock_set.side_effect = Exception("Storage failed")
            data = {"key": "test_key", "value": "test_value"}

            response = await async_client.post("/data", json=data)

            assert response.status_code == 503
            result = response.json()
            assert "Internal server error" in result["detail"]

    @pytest.mark.asyncio
    async def test_get_data_success(self, async_client):
        """Test successful data retrieval."""
        with patch.object(RedisClientManager, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = "test_value"

            response = await async_client.get("/data/test_key")

            assert response.status_code == 200
            result = response.json()
            assert result["status"] == "success"
            assert result["data"] == "test_value"
            mock_get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_data_not_found(self, async_client):
        """Test data retrieval when key not found."""
        with patch.object(RedisClientManager, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            response = await async_client.get("/data/test_key")

            assert response.status_code == 404
            result = response.json()
            assert "Service unavailable" in result["detail"]

    @pytest.mark.asyncio
    async def test_get_data_failure(self, async_client):
        """Test data retrieval failure."""
        with patch.object(RedisClientManager, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Retrieval failed")

            response = await async_client.get("/data/test_key")

            assert response.status_code == 503
            result = response.json()
            assert "Internal server error" in result["detail"]