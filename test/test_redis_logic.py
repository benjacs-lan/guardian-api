import unittest
from unittest.mock import Mock, patch
from src.app.redis_logic import RedisClientManager
from src.app.services.guardian_service import GuardianService


class TestRedisClientManager(unittest.TestCase):
    def test_get_client(self):
        manager = RedisClientManager()
        client = manager.get_client()
        self.assertIsNotNone(client)
        self.assertEqual(client, manager.client)

    def test_set_client(self):
        manager = RedisClientManager()
        client = Mock()
        manager.set_client(client)
        self.assertEqual(client, manager.client)

    def test_delete_client(self):
        manager = RedisClientManager()
        client = Mock()
        manager.set_client(client)
        manager.delete_client()
        self.assertIsNone(manager.client)

    def test_get_client_with_no_client(self):
        manager = RedisClientManager()
        client = manager.get_client()
        self.assertIsNone(client)   
        