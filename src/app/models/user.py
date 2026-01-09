"""
User model for the Guardian API.

This module defines the SQLAlchemy model for users.
"""

from sqlalchemy import Column, Integer, String
from ..config import Base


class User(Base):
    """
    SQLAlchemy model for users.

    Attributes:
        id (int): Primary key
        nombre (str): User's name
        email (str): User's email, unique
        rol (str): User's role
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    rol = Column(String)