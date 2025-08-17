"""
Transaction Management for Persistence Service

This module provides transaction context management for business-level transactions.
"""

from contextlib import contextmanager
from typing import Generator
import logging

from .database import DatabaseManager
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize logger
logger = get_logger(__name__)

class TransactionManager:
    """Manages business-level transactions for the Persistence Service."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    @contextmanager
    def transaction(self) -> Generator:
        """Context manager for business-level transactions."""
        with TracerContextManager.start_span("TransactionManager.transaction"):
            logger.info("Starting business-level transaction")
            
            conn = None
            try:
                conn = self.db_manager.get_connection()
                conn.autocommit = False
                logger.info("Database transaction started")
                yield conn
                conn.commit()
                logger.info("Database transaction committed successfully")
            except Exception as e:
                if conn:
                    conn.rollback()
                    logger.error("Database transaction rolled back due to error", extra={"error": str(e)})
                raise
            finally:
                if conn:
                    conn.autocommit = True
                    self.db_manager.put_connection(conn)
                    logger.info("Database connection returned to pool")