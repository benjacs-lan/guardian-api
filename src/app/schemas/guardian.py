"""
Pydantic schemas for Guardian API.

This module defines request and response schemas for guardian operations.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class GuardianBase(BaseModel):
    """
    Base schema for Guardian.

    Attributes:
        user_id (int): ID of the associated user
        ubicacion (str): Guardian's location
        estado (str): Guardian's status
    """
    user_id: int = Field(..., gt=0, description="User ID must be positive")
    ubicacion: str = Field(..., min_length=1, max_length=255, description="Location is required")
    estado: str = Field(..., min_length=1, max_length=50, description="Status is required")

    @field_validator('estado')
    @classmethod
    def validate_estado(cls, v):
        """Validate estado is one of allowed values."""
        allowed_states = ['active', 'inactive', 'alert', 'offline']
        if v not in allowed_states:
            raise ValueError(f'estado must be one of: {", ".join(allowed_states)}')
        return v

    @field_validator('ubicacion')
    @classmethod
    def validate_ubicacion(cls, v):
        """Validate ubicacion doesn't contain dangerous characters."""
        if '<' in v or '>' in v or 'script' in v.lower():
            raise ValueError('ubicacion contains invalid characters')
        return v.strip()


class CreateGuardian(GuardianBase):
    """
    Schema for creating a new guardian.
    """
    pass


class UpdateGuardian(BaseModel):
    """
    Schema for updating an existing guardian.

    Attributes:
        ubicacion (str, optional): New location
        estado (str, optional): New status
    """
    ubicacion: str | None = None
    estado: str | None = None


class GuardianResponse(GuardianBase):
    """
    Schema for guardian response.

    Attributes:
        id (int): Guardian ID
        timestamp (datetime): Creation timestamp
    """
    id: int
    timestamp: datetime