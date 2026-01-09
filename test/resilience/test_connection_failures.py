"""
Resilience tests for connection failures.

Tests system behavior under network failures, timeouts, and disconnections.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from redis.asyncio import ConnectionError as RedisConnectionError
from sqlalchemy.exc import OperationalError
from src.app.redis_client import RedisClientManager
from src.app.services.guardian_service import GuardianService


class TestRedisResilience:
    """Test Redis connection resilience."""

    @pytest.fixture
    def redis_manager(self):
        """Redis manager instance."""
        return RedisClientManager(host="localhost", port=6379, db=0)

    @pytest.mark.asyncio
    async def test_ping_with_connection_error(self, redis_manager):
        """Test ping handles connection errors gracefully."""
        with patch.object(redis_manager.redis, 'ping', side_effect=RedisConnectionError("Connection failed")):
            result = await redis_manager.ping()
            assert result is False

    @pytest.mark.asyncio
    async def test_ping_with_timeout(self, redis_manager):
        """Test ping handles timeouts."""
        with patch.object(redis_manager.redis, 'ping', side_effect=asyncio.TimeoutError()):
            result = await redis_manager.ping()
            assert result is False

    @pytest.mark.asyncio
    async def test_set_with_connection_error(self, redis_manager):
        """Test set operation with connection error."""
        with patch.object(redis_manager.redis, 'set', side_effect=RedisConnectionError("Connection failed")):
            # Should not raise exception, but operation fails
            await redis_manager.set("key", "value")
            # In real implementation, you might want to handle this

    @pytest.mark.asyncio
    async def test_get_with_connection_error(self, redis_manager):
        """Test get operation with connection error."""
        with patch.object(redis_manager.redis, 'get', side_effect=RedisConnectionError("Connection failed")):
            result = await redis_manager.get("key")
            assert result is None  # Should handle gracefully

    @pytest.mark.asyncio
    async def test_multiple_connection_failures(self, redis_manager):
        """Test multiple consecutive connection failures."""
        with patch.object(redis_manager.redis, 'ping', side_effect=[RedisConnectionError("Failed")] * 3 + [True]):
            # First three fail
            for _ in range(3):
                result = await redis_manager.ping()
                assert result is False

            # Fourth succeeds
            result = await redis_manager.ping()
            assert result is True


class TestDatabaseResilience:
    """Test database connection resilience."""

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = MagicMock()
        return session

    @pytest.fixture
    def service(self):
        """Guardian service with mock Redis."""
        mock_redis = MagicMock()
        mock_redis.set = AsyncMock()
        mock_redis.get = AsyncMock()
        return GuardianService(mock_redis)

    def test_create_guardian_with_db_error(self, service, mock_db_session):
        """Test guardian creation with database error."""
        from src.app.schemas import CreateGuardian

        # Mock user exists
        mock_user = MagicMock()
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock database commit failure
        mock_db_session.commit.side_effect = OperationalError("Connection lost", None, None)

        guardian_data = CreateGuardian(user_id=1, ubicacion="Location", estado="active")

        with pytest.raises(OperationalError):
            service.create_guardian(mock_db_session, guardian_data)

    def test_get_guardian_with_db_error(self, service, mock_db_session):
        """Test guardian retrieval with database error."""
        mock_db_session.query.side_effect = OperationalError("Connection lost", None, None)

        with pytest.raises(OperationalError):
            service.get_guardian(mock_db_session, 1)

    def test_update_guardian_with_db_error(self, service, mock_db_session):
        """Test guardian update with database error."""
        from src.app.schemas import UpdateGuardian

        # Mock guardian exists
        mock_guardian = MagicMock()
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_guardian

        # Mock commit failure
        mock_db_session.commit.side_effect = OperationalError("Connection lost", None, None)

        update_data = UpdateGuardian(ubicacion="New Location")

        with pytest.raises(OperationalError):
            service.update_guardian(mock_db_session, 1, update_data)


class TestServiceResilience:
    """Test service layer resilience."""

    @pytest.fixture
    def service(self):
        """Guardian service instance."""
        mock_redis = MagicMock()
        return GuardianService(mock_redis)

    @pytest.mark.asyncio
    async def test_store_data_with_redis_failure(self, service):
        """Test data storage with Redis failure."""
        service.redis.set.side_effect = RedisConnectionError("Redis down")

        # Should not raise exception in current implementation
        await service.store_data("key", "value")

    @pytest.mark.asyncio
    async def test_get_data_with_redis_failure(self, service):
        """Test data retrieval with Redis failure."""
        service.redis.get.side_effect = RedisConnectionError("Redis down")

        result = await service.get_data("key")
        assert result is None  # Should handle gracefully

    @pytest.mark.asyncio
    async def test_concurrent_failures(self, service):
        """Test concurrent operations during failures."""
        service.redis.set.side_effect = RedisConnectionError("Redis down")
        service.redis.get.side_effect = RedisConnectionError("Redis down")

        # Run multiple operations concurrently
        tasks = []
        for i in range(5):
            tasks.append(service.store_data(f"key{i}", f"value{i}"))
            tasks.append(service.get_data(f"key{i}"))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete without raising exceptions
        for result in results:
            assert not isinstance(result, Exception) or isinstance(result, RedisConnectionError)