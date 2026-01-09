"""
Unit tests for GuardianService.

Tests isolated service operations using mocks for database and Redis.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from src.app.services.guardian_service import GuardianService
from src.app.schemas import CreateGuardian, UpdateGuardian
from src.app.models import User, Guardian


class TestGuardianService:
    """Test cases for GuardianService."""

    @pytest.fixture
    def mock_redis(self):
        """Mock Redis client manager."""
        redis = MagicMock()
        redis.set = AsyncMock()
        redis.get = AsyncMock()
        return redis

    @pytest.fixture
    def service(self, mock_redis):
        """Fixture for GuardianService instance."""
        return GuardianService(mock_redis)

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = MagicMock()
        return session

    @pytest.mark.asyncio
    async def test_store_data_success(self, service, mock_redis):
        """Test successful data storage."""
        await service.store_data("key", "value")

        mock_redis.set.assert_called_once_with("key", "value", ttl=3600)

    @pytest.mark.asyncio
    async def test_get_data_success(self, service, mock_redis):
        """Test successful data retrieval."""
        mock_redis.get.return_value = "value"

        result = await service.get_data("key")

        assert result == "value"
        mock_redis.get.assert_called_once_with("key")

    @pytest.mark.asyncio
    async def test_get_data_not_found(self, service, mock_redis):
        """Test data retrieval when not found."""
        mock_redis.get.return_value = None

        result = await service.get_data("key")

        assert result is None
        mock_redis.get.assert_called_once_with("key")

    def test_create_guardian_success(self, service, mock_db_session):
        """Test successful guardian creation."""
        # Mock user query
        mock_user = MagicMock(spec=User)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

        # Mock guardian creation
        mock_guardian = MagicMock(spec=Guardian)
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()
        mock_db_session.refresh = MagicMock()

        guardian_data = CreateGuardian(user_id=1, ubicacion="Location", estado="active")

        with patch('src.app.services.guardian_service.Guardian', return_value=mock_guardian):
            result = service.create_guardian(mock_db_session, guardian_data)

            assert result == mock_guardian
            mock_db_session.add.assert_called_once_with(mock_guardian)
            mock_db_session.commit.assert_called_once()
            mock_db_session.refresh.assert_called_once_with(mock_guardian)

    def test_create_guardian_user_not_found(self, service, mock_db_session):
        """Test guardian creation when user not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        guardian_data = CreateGuardian(user_id=999, ubicacion="Location", estado="active")

        with pytest.raises(ValueError, match="User not found"):
            service.create_guardian(mock_db_session, guardian_data)

    def test_get_guardian_success(self, service, mock_db_session):
        """Test successful guardian retrieval."""
        mock_guardian = MagicMock(spec=Guardian)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_guardian

        result = service.get_guardian(mock_db_session, 1)

        assert result == mock_guardian

    def test_get_guardian_not_found(self, service, mock_db_session):
        """Test guardian retrieval when not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = service.get_guardian(mock_db_session, 1)

        assert result is None

    def test_get_guardians_paginated(self, service, mock_db_session):
        """Test guardians list retrieval with pagination."""
        mock_guardians = [MagicMock(spec=Guardian), MagicMock(spec=Guardian)]
        query_mock = mock_db_session.query.return_value
        query_mock.offset.return_value.limit.return_value.all.return_value = mock_guardians

        result = service.get_guardians(mock_db_session, skip=10, limit=5)

        assert result == mock_guardians
        query_mock.offset.assert_called_once_with(10)
        query_mock.offset.return_value.limit.assert_called_once_with(5)

    def test_update_guardian_success(self, service, mock_db_session):
        """Test successful guardian update."""
        mock_guardian = MagicMock(spec=Guardian)
        mock_guardian.ubicacion = "Old Location"
        mock_guardian.estado = "inactive"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_guardian

        update_data = UpdateGuardian(ubicacion="New Location")

        result = service.update_guardian(mock_db_session, 1, update_data)

        assert result == mock_guardian
        assert mock_guardian.ubicacion == "New Location"
        assert mock_guardian.estado == "inactive"  # unchanged
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_guardian)

    def test_update_guardian_not_found(self, service, mock_db_session):
        """Test guardian update when not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        update_data = UpdateGuardian(ubicacion="New Location")

        result = service.update_guardian(mock_db_session, 1, update_data)

        assert result is None

    def test_delete_guardian_success(self, service, mock_db_session):
        """Test successful guardian deletion."""
        mock_guardian = MagicMock(spec=Guardian)
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_guardian

        result = service.delete_guardian(mock_db_session, 1)

        assert result is True
        mock_db_session.delete.assert_called_once_with(mock_guardian)
        mock_db_session.commit.assert_called_once()

    def test_delete_guardian_not_found(self, service, mock_db_session):
        """Test guardian deletion when not found."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = service.delete_guardian(mock_db_session, 1)

        assert result is False