"""
Configuration for Persistence Service

This module handles database configuration and connection settings.
"""

import os
from typing import Optional


class DatabaseConfig:
    """Configuration class for database connection settings."""
    
    def __init__(self):
        self.host: str = os.getenv('DB_HOST', '192.168.88.20')
        self.port: int = int(os.getenv('DB_PORT', 5432))
        self.database: str = os.getenv('DB_NAME', 'maindb')
        self.user: str = os.getenv('DB_USER', 'admin')
        self.password: str = os.getenv('DB_PASSWORD', 'password')
        self.min_connections: int = int(os.getenv('DB_MIN_CONNECTIONS', 1))
        self.max_connections: int = int(os.getenv('DB_MAX_CONNECTIONS', 10))
    
    @property
    def connection_string(self) -> str:
        """Generate the PostgreSQL connection string."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    def __str__(self) -> str:
        return f"DatabaseConfig(host={self.host}, port={self.port}, database={self.database})"