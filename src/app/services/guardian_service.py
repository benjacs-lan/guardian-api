"""
Guardian service layer.

This module provides business logic for guardian operations, including CRUD operations,
validations, and Redis caching integration.
"""

from sqlalchemy.orm import Session
from ..models import Guardian, User
from ..schemas import CreateGuardian, UpdateGuardian, GuardianResponse
from ..redis_client import RedisClientManager
from ..settings import CACHE_TTL
import json


class GuardianService:
    """
    Service class for guardian business logic.

    Attributes:
        redis (RedisClientManager): Redis client for caching
    """

    def __init__(self, redis_manager: RedisClientManager):
        """
        Initialize the service with Redis manager.

        Args:
            redis_manager (RedisClientManager): Redis client manager
        """
        self.redis = redis_manager

    async def store_data(self, key: str, value: str) -> None:
        """
        Store data in Redis cache.

        Args:
            key (str): Cache key
            value (str): Value to store
        """
        await self.redis.set(key, value, ttl=CACHE_TTL)

    async def get_data(self, key: str) -> str | None:
        """
        Retrieve data from Redis cache.

        Args:
            key (str): Cache key

        Returns:
            str | None: Cached value or None
        """
        return await self.redis.get(key)

    def create_guardian(self, db: Session, guardian: CreateGuardian) -> Guardian:
        """
        Create a new guardian.

        Args:
            db (Session): Database session
            guardian (CreateGuardian): Guardian data

        Returns:
            Guardian: Created guardian instance
        """
        # Validate user exists
        user = db.query(User).filter(User.id == guardian.user_id).first()
        if not user:
            raise ValueError("User not found")

        db_guardian = Guardian(**guardian.model_dump())
        db.add(db_guardian)
        db.commit()
        db.refresh(db_guardian)
        return db_guardian

    def get_guardian(self, db: Session, guardian_id: int) -> Guardian | None:
        """
        Get a guardian by ID.

        Args:
            db (Session): Database session
            guardian_id (int): Guardian ID

        Returns:
            Guardian | None: Guardian instance or None
        """
        return db.query(Guardian).filter(Guardian.id == guardian_id).first()

    def get_guardians(self, db: Session, skip: int = 0, limit: int = 10) -> list[Guardian]:
        """
        Get a list of guardians with pagination.

        Args:
            db (Session): Database session
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return

        Returns:
            list[Guardian]: List of guardians
        """
        return db.query(Guardian).offset(skip).limit(limit).all()

    def update_guardian(self, db: Session, guardian_id: int, guardian_update: UpdateGuardian) -> Guardian | None:
        """
        Update an existing guardian.

        Args:
            db (Session): Database session
            guardian_id (int): Guardian ID
            guardian_update (UpdateGuardian): Update data

        Returns:
            Guardian | None: Updated guardian or None if not found
        """
        db_guardian = self.get_guardian(db, guardian_id)
        if not db_guardian:
            return None

        update_data = guardian_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_guardian, field, value)

        db.commit()
        db.refresh(db_guardian)
        return db_guardian

    def delete_guardian(self, db: Session, guardian_id: int) -> bool:
        """
        Delete a guardian.

        Args:
            db (Session): Database session
            guardian_id (int): Guardian ID

        Returns:
            bool: True if deleted, False if not found
        """
        db_guardian = self.get_guardian(db, guardian_id)
        if not db_guardian:
            return False

        db.delete(db_guardian)
        db.commit()
        return True