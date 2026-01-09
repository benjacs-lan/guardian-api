"""
Redis client manager for asynchronous operations.

This module provides a Redis client manager with connection pooling for async operations.
"""

import redis.asyncio as redis
from .config import settings


class RedisClientManager:
    """
    Manager for Redis connections with async support.

    Attributes:
        redis (redis.Redis): Async Redis client instance
    """

    def __init__(self, host: str = None, port: int = None, db: int = None):
        """
        Initialize the Redis client.

        Args:
            host (str, optional): Redis host. Defaults to settings.redis_host
            port (int, optional): Redis port. Defaults to settings.redis_port
            db (int, optional): Redis database. Defaults to settings.redis_db
        """
        self.redis = redis.Redis(
            host=host or settings.redis_host,
            port=port or settings.redis_port,
            db=db or settings.redis_db,
            decode_responses=True
        )

    async def ping(self) -> bool:
        """
        Ping the Redis server.

        Returns:
            bool: True if connected, False otherwise
        """
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False

    async def set(self, key: str, value: str, ttl: int = None) -> None:
        """
        Set a key-value pair in Redis.

        Args:
            key (str): Key
            value (str): Value
            ttl (int, optional): Time to live in seconds
        """
        await self.redis.set(key, value, ex=ttl)

    async def get(self, key: str) -> str | None:
        """
        Get a value from Redis.

        Args:
            key (str): Key

        Returns:
            str | None: Value if exists, None otherwise
        """
        return await self.redis.get(key)

    async def delete(self, key: str) -> int:
        """
        Delete a key from Redis.

        Args:
            key (str): Key

        Returns:
            int: Number of keys deleted
        """
        return await self.redis.delete(key)

    async def close(self) -> None:
        """
        Close the Redis connection.
        """
        await self.redis.close()