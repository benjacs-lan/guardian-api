"""
Unit tests for SQLAlchemy models.

Tests model creation and relationships.
"""

import pytest
from src.app.models import User, Guardian, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class TestUserModel:
    """Test cases for User model."""

    @pytest.fixture
    def db_session(self):
        """In-memory database session for testing."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)

    def test_user_creation(self, db_session):
        """Test user model creation."""
        user = User(
            nombre="John Doe",
            email="john@example.com",
            rol="guardian"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.nombre == "John Doe"
        assert user.email == "john@example.com"
        assert user.rol == "guardian"

    def test_user_unique_email(self, db_session):
        """Test unique email constraint."""
        user1 = User(
            nombre="John Doe",
            email="john@example.com",
            rol="guardian"
        )
        user2 = User(
            nombre="Jane Doe",
            email="john@example.com",  # Same email
            rol="admin"
        )
        db_session.add(user1)
        db_session.commit()

        db_session.add(user2)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestGuardianModel:
    """Test cases for Guardian model."""

    @pytest.fixture
    def db_session(self):
        """In-memory database session for testing."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
            Base.metadata.drop_all(bind=engine)

    def test_guardian_creation(self, db_session):
        """Test guardian model creation."""
        # Create user first
        user = User(
            nombre="John Doe",
            email="john@example.com",
            rol="guardian"
        )
        db_session.add(user)
        db_session.commit()

        guardian = Guardian(
            user_id=user.id,
            ubicacion="Main Entrance",
            estado="active"
        )
        db_session.add(guardian)
        db_session.commit()
        db_session.refresh(guardian)

        assert guardian.id is not None
        assert guardian.user_id == user.id
        assert guardian.ubicacion == "Main Entrance"
        assert guardian.estado == "active"
        assert guardian.timestamp is not None
        assert guardian.user == user

    def test_guardian_foreign_key_constraint(self, db_session):
        """Test foreign key constraint."""
        guardian = Guardian(
            user_id=999,  # Non-existent user
            ubicacion="Location",
            estado="active"
        )
        db_session.add(guardian)
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()