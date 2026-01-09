"""
Unit tests for RedisClientManager.

Tests isolated Redis client operations using mocks.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.app.redis_client import RedisClientManager


class TestRedisClientManager:
    """Test cases for RedisClientManager."""

    @pytest.fixture
    def redis_manager(self):
        """Fixture for RedisClientManager instance."""
        return RedisClientManager(host="localhost", port=6379, db=0)

    @pytest.mark.asyncio
    async def test_ping_success(self, redis_manager):
        """Test successful ping."""
        with patch.object(redis_manager.redis, 'ping', new_callable=AsyncMock) as mock_ping:
            mock_ping.return_value = True

            result = await redis_manager.ping()

            assert result is True
            mock_ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_ping_failure(self, redis_manager):
        """Test ping failure."""
        with patch.object(redis_manager.redis, 'ping', new_callable=AsyncMock) as mock_ping:
            mock_ping.side_effect = Exception("Connection failed")

            result = await redis_manager.ping()

            assert result is False
            mock_ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_success(self, redis_manager):
        """Test successful set operation."""
        with patch.object(redis_manager.redis, 'set', new_callable=AsyncMock) as mock_set:
            await redis_manager.set("key", "value", ttl=60)

            mock_set.assert_called_once_with("key", "value", ex=60)

    @pytest.mark.asyncio
    async def test_set_without_ttl(self, redis_manager):
        """Test set operation without TTL."""
        with patch.object(redis_manager.redis, 'set', new_callable=AsyncMock) as mock_set:
            await redis_manager.set("key", "value")

            mock_set.assert_called_once_with("key", "value", ex=None)

    @pytest.mark.asyncio
    async def test_get_success(self, redis_manager):
        """Test successful get operation."""
        with patch.object(redis_manager.redis, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = "value"

            result = await redis_manager.get("key")

            assert result == "value"
            mock_get.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_get_not_found(self, redis_manager):
        """Test get operation when key not found."""
        with patch.object(redis_manager.redis, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await redis_manager.get("key")

            assert result is None
            mock_get.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_delete_success(self, redis_manager):
        """Test successful delete operation."""
        with patch.object(redis_manager.redis, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = 1

            result = await redis_manager.delete("key")

            assert result == 1
            mock_delete.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_close(self, redis_manager):
        """Test close operation."""
        with patch.object(redis_manager.redis, 'close', new_callable=AsyncMock) as mock_close:
            await redis_manager.close()

            mock_close.assert_called_once()

    def test_initialization_with_defaults(self):
        """Test initialization with default values."""
        from src.app.config import settings
        manager = RedisClientManager()

        assert manager.redis is not None
        # Check that it uses settings values (mocked in tests)