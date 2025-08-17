"""
Task History Repository for Persistence Service

This module provides data access methods for task history records.
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import logging

from ..models.task import TaskHistoryRecord
from ..database import DatabaseManager
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize logger
logger = get_logger(__name__)

class TaskHistoryRepository:
    """Repository class for task history-related database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_task_history_record(self, task_id: UUID, version_number: int, 
                                 data_snapshot: Dict[str, Any]) -> UUID:
        """Create a new task history record and return its ID."""
        with TracerContextManager.start_span("TaskHistoryRepository.create_task_history_record"):
            logger.info("Creating new task history record", extra={
                "task_id": str(task_id),
                "version_number": version_number
            })
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO task_history (task_id, version_number, data_snapshot)
                        VALUES (%s, %s, %s)
                        RETURNING id
                    """, (task_id, version_number, json.dumps(data_snapshot)))
                    
                    history_id = cur.fetchone()[0]
                    logger.info("Task history record created successfully", extra={"history_id": str(history_id)})
                    return history_id
    
    def get_task_history_by_id(self, history_id: UUID) -> Optional[TaskHistoryRecord]:
        """Get a task history record by its ID."""
        with TracerContextManager.start_span("TaskHistoryRepository.get_task_history_by_id"):
            logger.info("Fetching task history record by ID", extra={"history_id": str(history_id)})
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, task_id, version_number, data_snapshot, created_at
                        FROM task_history
                        WHERE id = %s
                    """, (history_id,))
                    
                    row = cur.fetchone()
                    if row:
                        history_record = TaskHistoryRecord(
                            id=row[0],
                            task_id=row[1],
                            version_number=row[2],
                            data_snapshot=row[3],
                            created_at=row[4]
                        )
                        logger.info("Task history record found", extra={"history_id": str(history_id)})
                        return history_record
                    else:
                        logger.info("Task history record not found", extra={"history_id": str(history_id)})
                        return None
    
    def get_task_history_by_task_id(self, task_id: UUID) -> List[TaskHistoryRecord]:
        """Get all history records for a specific task, ordered by version number."""
        with TracerContextManager.start_span("TaskHistoryRepository.get_task_history_by_task_id"):
            logger.info("Fetching task history records by task ID", extra={"task_id": str(task_id)})
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, task_id, version_number, data_snapshot, created_at
                        FROM task_history
                        WHERE task_id = %s
                        ORDER BY version_number ASC
                    """, (task_id,))
                    
                    history_records = []
                    for row in cur.fetchall():
                        history_record = TaskHistoryRecord(
                            id=row[0],
                            task_id=row[1],
                            version_number=row[2],
                            data_snapshot=row[3],
                            created_at=row[4]
                        )
                        history_records.append(history_record)
                    
                    logger.info("Task history records retrieved", extra={"count": len(history_records)})
                    return history_records
    
    def get_latest_task_history(self, task_id: UUID) -> Optional[TaskHistoryRecord]:
        """Get the latest history record for a specific task."""
        with TracerContextManager.start_span("TaskHistoryRepository.get_latest_task_history"):
            logger.info("Fetching latest task history record", extra={"task_id": str(task_id)})
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, task_id, version_number, data_snapshot, created_at
                        FROM task_history
                        WHERE task_id = %s
                        ORDER BY version_number DESC
                        LIMIT 1
                    """, (task_id,))
                    
                    row = cur.fetchone()
                    if row:
                        history_record = TaskHistoryRecord(
                            id=row[0],
                            task_id=row[1],
                            version_number=row[2],
                            data_snapshot=row[3],
                            created_at=row[4]
                        )
                        logger.info("Latest task history record found", extra={"history_id": str(history_record.id)})
                        return history_record
                    else:
                        logger.info("No task history records found", extra={"task_id": str(task_id)})
                        return None