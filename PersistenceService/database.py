"""
Database Connection Management for Persistence Service

This module manages the PostgreSQL connection pool and provides
database session management.
"""

import psycopg2
from psycopg2 import pool
from contextlib import contextmanager
from typing import Generator, Optional
import logging

from .config import DatabaseConfig
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize logger
logger = get_logger(__name__)

class DatabaseManager:
    """Manages database connections and connection pooling."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.connection_pool: Optional[pool.ThreadedConnectionPool] = None
        self._initialize_pool()
    
    def _initialize_pool(self) -> None:
        """Initialize the connection pool."""
        with TracerContextManager.start_span("DatabaseManager._initialize_pool"):
            try:
                self.connection_pool = pool.ThreadedConnectionPool(
                    self.config.min_connections,
                    self.config.max_connections,
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.database,
                    user=self.config.user,
                    password=self.config.password
                )
                logger.info("Database connection pool initialized", 
                          extra={"min_connections": self.config.min_connections, 
                                "max_connections": self.config.max_connections})
            except Exception as e:
                logger.error("Failed to initialize database connection pool", 
                           extra={"error": str(e)})
                raise
    
    def get_connection(self):
        """Get a connection from the pool."""
        if not self.connection_pool:
            raise RuntimeError("Database connection pool not initialized")
        return self.connection_pool.getconn()
    
    def put_connection(self, conn) -> None:
        """Return a connection to the pool."""
        if self.connection_pool:
            self.connection_pool.putconn(conn)
    
    def close_all_connections(self) -> None:
        """Close all connections in the pool."""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("All database connections closed")
    
    @contextmanager
    def get_db_session(self) -> Generator:
        """Context manager for database sessions."""
        conn = None
        try:
            conn = self.get_connection()
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error("Database session error", extra={"error": str(e)})
            raise
        finally:
            if conn:
                conn.commit()
                self.put_connection(conn)