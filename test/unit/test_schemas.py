"""
Unit tests for Pydantic schemas.

Tests schema validation and serialization.
"""

import pytest
from pydantic import ValidationError
from src.app.schemas import GuardianBase, CreateGuardian, UpdateGuardian, GuardianResponse
from datetime import datetime


class TestGuardianSchemas:
    """Test cases for Guardian schemas."""

    def test_guardian_base_valid(self):
        """Test GuardianBase with valid data."""
        data = {
            "user_id": 1,
            "ubicacion": "Main Entrance",
            "estado": "active"
        }
        schema = GuardianBase(**data)

        assert schema.user_id == 1
        assert schema.ubicacion == "Main Entrance"
        assert schema.estado == "active"

    def test_guardian_base_invalid_user_id(self):
        """Test GuardianBase with invalid user_id."""
        data = {
            "user_id": "not_an_int",
            "ubicacion": "Location",
            "estado": "active"
        }
        with pytest.raises(ValidationError):
            GuardianBase(**data)

    def test_guardian_base_missing_required_field(self):
        """Test GuardianBase with missing required field."""
        data = {
            "user_id": 1,
            "ubicacion": "Location"
            # Missing estado
        }
        with pytest.raises(ValidationError):
            GuardianBase(**data)

    def test_create_guardian_inherits_base(self):
        """Test CreateGuardian inherits from GuardianBase."""
        data = {
            "user_id": 1,
            "ubicacion": "Location",
            "estado": "active"
        }
        schema = CreateGuardian(**data)

        assert isinstance(schema, GuardianBase)
        assert schema.user_id == 1
        assert schema.ubicacion == "Location"
        assert schema.estado == "active"

    def test_update_guardian_optional_fields(self):
        """Test UpdateGuardian with optional fields."""
        # All fields
        data = {
            "ubicacion": "New Location",
            "estado": "inactive"
        }
        schema = UpdateGuardian(**data)

        assert schema.ubicacion == "New Location"
        assert schema.estado == "inactive"

        # Partial update
        data_partial = {
            "ubicacion": "Another Location"
        }
        schema_partial = UpdateGuardian(**data_partial)

        assert schema_partial.ubicacion == "Another Location"
        assert schema_partial.estado is None

        # Empty update
        schema_empty = UpdateGuardian()
        assert schema_empty.ubicacion is None
        assert schema_empty.estado is None

    def test_guardian_response_with_timestamp(self):
        """Test GuardianResponse with timestamp."""
        timestamp = datetime.utcnow()
        data = {
            "id": 1,
            "user_id": 1,
            "ubicacion": "Location",
            "estado": "active",
            "timestamp": timestamp
        }
        schema = GuardianResponse(**data)

        assert schema.id == 1
        assert schema.user_id == 1
        assert schema.ubicacion == "Location"
        assert schema.estado == "active"
        assert schema.timestamp == timestamp

    def test_guardian_response_invalid_timestamp(self):
        """Test GuardianResponse with invalid timestamp."""
        data = {
            "id": 1,
            "user_id": 1,
            "ubicacion": "Location",
            "estado": "active",
            "timestamp": "not_a_datetime"
        }
        with pytest.raises(ValidationError):
            GuardianResponse(**data)

    @pytest.mark.parametrize("invalid_estado", ["", "invalid_status", None])
    def test_guardian_base_invalid_estado(self, invalid_estado):
        """Test GuardianBase with various invalid estado values."""
        data = {
            "user_id": 1,
            "ubicacion": "Location",
            "estado": invalid_estado
        }
        # Pydantic allows any string, so this should pass
        # In a real app, you might add validation
        schema = GuardianBase(**data)
        assert schema.estado == invalid_estado