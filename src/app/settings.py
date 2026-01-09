"""
Global settings and constants for the Guardian API application.

This module contains application-wide constants and enumerations.
"""

# User roles
USER_ROLES = ["admin", "guardian", "user"]

# Guardian statuses
GUARDIAN_STATUSES = ["active", "inactive", "alert", "offline"]

# Default pagination
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100

# Cache TTL in seconds
CACHE_TTL = 3600  # 1 hour

# API version
API_VERSION = "1.0.0"