"""
Shared fixtures and configuration for pytest.
"""

import os
import pytest
import asyncio
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.config import Base, SessionLocal
from src.app.models import User, Guardian


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def postgres_container():
    """PostgreSQL container for integration tests."""
    with PostgresContainer("postgres:13-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def redis_container():
    """Redis container for integration tests."""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


@pytest.fixture(scope="function")
def db_session(postgres_container):
    """Database session fixture for tests."""
    # Override the database URL for tests
    test_db_url = postgres_container.get_connection_url()
    engine = create_engine(test_db_url)

    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def redis_client(redis_container):
    """Redis client fixture for tests."""
    from src.app.redis_client import RedisClientManager
    host, port = redis_container.get_container_host_ip(), redis_container.get_exposed_port(6379)
    client = RedisClientManager(host=host, port=port, db=0)
    yield client
    # Clean up
    asyncio.run(client.close())


@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "id": 1,
        "nombre": "Test User",
        "email": "test@example.com",
        "rol": "guardian"
    }


@pytest.fixture
def sample_guardian():
    """Sample guardian data."""
    return {
        "id": 1,
        "user_id": 1,
        "ubicacion": "Test Location",
        "estado": "active"
    }