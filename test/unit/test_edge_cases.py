"""
Edge case tests for various components.

Tests invalid inputs, boundary conditions, and unexpected behaviors.
"""

import pytest
from pydantic import ValidationError
from unittest.mock import MagicMock, AsyncMock, patch
from src.app.schemas import CreateGuardian, UpdateGuardian, GuardianResponse
from src.app.services.guardian_service import GuardianService
from src.app.redis_client import RedisClientManager
from datetime import datetime


class TestSchemaEdgeCases:
    """Test edge cases for Pydantic schemas."""

    @pytest.mark.parametrize("user_id", [-1, 0, 999999999])
    def test_guardian_schemas_with_extreme_user_ids(self, user_id):
        """Test schemas with extreme user ID values."""
        data = {
            "user_id": user_id,
            "ubicacion": "Location",
            "estado": "active"
        }

        if user_id > 0:
            schema = CreateGuardian(**data)
            assert schema.user_id == user_id
        else:
            with pytest.raises(ValidationError):
                CreateGuardian(**data)

    @pytest.mark.parametrize("ubicacion", ["", "A" * 1000, "Location\nwith\nnewlines", "Location\twith\ttabs"])
    def test_guardian_schemas_with_various_locations(self, ubicacion):
        """Test schemas with various location strings."""
        data = {
            "user_id": 1,
            "ubicacion": ubicacion,
            "estado": "active"
        }

        schema = CreateGuardian(**data)
        assert schema.ubicacion == ubicacion

    @pytest.mark.parametrize("estado", ["", "A" * 100, "active", "inactive", "alert", "unknown"])
    def test_guardian_schemas_with_various_states(self, estado):
        """Test schemas with various state values."""
        data = {
            "user_id": 1,
            "ubicacion": "Location",
            "estado": estado
        }

        schema = CreateGuardian(**data)
        assert schema.estado == estado

    def test_update_guardian_with_empty_strings(self):
        """Test UpdateGuardian with empty strings."""
        data = {
            "ubicacion": "",
            "estado": ""
        }

        schema = UpdateGuardian(**data)
        assert schema.ubicacion == ""
        assert schema.estado == ""

    def test_guardian_response_with_future_timestamp(self):
        """Test GuardianResponse with future timestamp."""
        future_time = datetime(2030, 1, 1, 12, 0, 0)
        data = {
            "id": 1,
            "user_id": 1,
            "ubicacion": "Location",
            "estado": "active",
            "timestamp": future_time
        }

        schema = GuardianResponse(**data)
        assert schema.timestamp == future_time

    def test_guardian_response_with_past_timestamp(self):
        """Test GuardianResponse with past timestamp."""
        past_time = datetime(2000, 1, 1, 12, 0, 0)
        data = {
            "id": 1,
            "user_id": 1,
            "ubicacion": "Location",
            "estado": "active",
            "timestamp": past_time
        }

        schema = GuardianResponse(**data)
        assert schema.timestamp == past_time


class TestServiceEdgeCases:
    """Test edge cases for GuardianService."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client."""
        redis = MagicMock()
        redis.set = AsyncMock()
        redis.get = AsyncMock()
        return redis

    @pytest.fixture
    def service(self, mock_redis):
        """Guardian service instance."""
        return GuardianService(mock_redis)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = MagicMock()
        return session

    def test_create_guardian_with_nonexistent_user(self, service, mock_db_session):
        """Test creating guardian with nonexistent user."""
        from src.app.schemas import CreateGuardian

        # Mock user not found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        guardian_data = CreateGuardian(user_id=999, ubicacion="Location", estado="active")

        with pytest.raises(ValueError, match="User not found"):
            service.create_guardian(mock_db_session, guardian_data)

    def test_get_guardian_with_negative_id(self, service, mock_db_session):
        """Test getting guardian with negative ID."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = service.get_guardian(mock_db_session, -1)
        assert result is None

    def test_get_guardians_with_large_limit(self, service, mock_db_session):
        """Test getting guardians with very large limit."""
        mock_guardians = [MagicMock()] * 1000
        query_mock = mock_db_session.query.return_value
        query_mock.offset.return_value.limit.return_value.all.return_value = mock_guardians

        result = service.get_guardians(mock_db_session, skip=0, limit=10000)

        assert len(result) == 1000
        query_mock.offset.return_value.limit.assert_called_with(10000)

    def test_update_guardian_with_no_changes(self, service, mock_db_session):
        """Test updating guardian with no actual changes."""
        from src.app.schemas import UpdateGuardian

        mock_guardian = MagicMock()
        mock_guardian.ubicacion = "Location"
        mock_guardian.estado = "active"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_guardian

        update_data = UpdateGuardian()  # Empty update

        result = service.update_guardian(mock_db_session, 1, update_data)

        assert result == mock_guardian
        mock_db_session.commit.assert_called_once()

    def test_delete_guardian_twice(self, service, mock_db_session):
        """Test deleting the same guardian twice."""
        # First delete succeeds
        mock_guardian = MagicMock()
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_guardian

        result1 = service.delete_guardian(mock_db_session, 1)
        assert result1 is True

        # Second delete fails
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result2 = service.delete_guardian(mock_db_session, 1)
        assert result2 is False


class TestRedisEdgeCases:
    """Test edge cases for Redis operations."""

    @pytest.fixture
    def redis_manager(self):
        """Redis manager instance."""
        return RedisClientManager(host="localhost", port=6379, db=0)

    @pytest.mark.asyncio
    async def test_set_with_very_long_key(self, redis_manager):
        """Test setting with very long key."""
        long_key = "A" * 1000
        long_value = "B" * 10000

        with patch.object(redis_manager.redis, 'set', new_callable=AsyncMock) as mock_set:
            await redis_manager.set(long_key, long_value)

            mock_set.assert_called_once_with(long_key, long_value, ex=None)

    @pytest.mark.asyncio
    async def test_set_with_special_characters(self, redis_manager):
        """Test setting with special characters in key/value."""
        special_key = "key:with:colons"
        special_value = "value\nwith\nnewlines\tand\ttabs"

        with patch.object(redis_manager.redis, 'set', new_callable=AsyncMock) as mock_set:
            await redis_manager.set(special_key, special_value)

            mock_set.assert_called_once_with(special_key, special_value, ex=None)

    @pytest.mark.asyncio
    async def test_get_with_nonexistent_key(self, redis_manager):
        """Test getting nonexistent key."""
        with patch.object(redis_manager.redis, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None

            result = await redis_manager.get("nonexistent")

            assert result is None
            mock_get.assert_called_once_with("nonexistent")

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self, redis_manager):
        """Test deleting nonexistent key."""
        with patch.object(redis_manager.redis, 'delete', new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = 0  # No keys deleted

            result = await redis_manager.delete("nonexistent")

            assert result == 0
            mock_delete.assert_called_once_with("nonexistent")