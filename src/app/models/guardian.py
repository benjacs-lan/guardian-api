"""
Guardian model for the Guardian API.

This module defines the SQLAlchemy model for guardians.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..config import Base


class Guardian(Base):
    """
    SQLAlchemy model for guardians.

    Attributes:
        id (int): Primary key
        user_id (int): Foreign key to User
        ubicacion (str): Guardian's location
        estado (str): Guardian's status
        timestamp (datetime): Timestamp of the record
        user (User): Relationship to User
    """
    __tablename__ = "guardians"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ubicacion = Column(String)
    estado = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")