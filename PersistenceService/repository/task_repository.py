"""
Task Repository for Persistence Service

This module provides data access methods for tasks.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import logging

from ..models.task import TaskRecord
from ..database import DatabaseManager
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize logger
logger = get_logger(__name__)

class TaskRepository:
    """Repository class for task-related database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def create_task(self, workflow_id: UUID, assignee_id: str, 
                   input_data: Optional[Dict[str, Any]] = None,
                   parent_task_id: Optional[UUID] = None,
                   directives: Optional[Dict[str, Any]] = None) -> UUID:
        """Create a new task and return its ID."""
        with TracerContextManager.start_span("TaskRepository.create_task"):
            logger.info("Creating new task", extra={
                "workflow_id": str(workflow_id),
                "assignee_id": assignee_id
            })
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO tasks (workflow_id, assignee_id, input_data, parent_task_id, directives)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (str(workflow_id), assignee_id, json.dumps(input_data) if input_data else None, 
                          str(parent_task_id) if parent_task_id else None, json.dumps(directives) if directives else None))
                    
                    task_id = cur.fetchone()[0]
                    logger.info("Task created successfully", extra={"task_id": str(task_id)})
                    return task_id
    
    def get_task_by_id(self, task_id: UUID) -> Optional[TaskRecord]:
        """Get a task by its ID."""
        with TracerContextManager.start_span("TaskRepository.get_task_by_id"):
            logger.info("Fetching task by ID", extra={"task_id": str(task_id)})
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, workflow_id, assignee_id, status, input_data, result, 
                               directives, parent_task_id, created_at, updated_at
                        FROM tasks
                        WHERE id = %s
                    """, (str(task_id),))
                    
                    row = cur.fetchone()
                    if row:
                        task_record = TaskRecord(
                            id=row[0],
                            workflow_id=row[1],
                            assignee_id=row[2],
                            status=row[3],
                            input_data=row[4],
                            result=row[5],
                            directives=row[6],
                            parent_task_id=row[7],
                            created_at=row[8],
                            updated_at=row[9]
                        )
                        logger.info("Task found", extra={"task_id": str(task_id)})
                        return task_record
                    else:
                        logger.info("Task not found", extra={"task_id": str(task_id)})
                        return None
    
    def update_task_status(self, task_id: UUID, status: str, 
                          result: Optional[Dict[str, Any]] = None) -> bool:
        """Update task status and optionally result."""
        with TracerContextManager.start_span("TaskRepository.update_task_status"):
            logger.info("Updating task status", extra={
                "task_id": str(task_id),
                "status": status
            })
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE tasks
                        SET status = %s, result = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (status, json.dumps(result) if result else None, str(task_id)))
                    
                    updated = cur.rowcount > 0
                    if updated:
                        logger.info("Task status updated successfully", extra={"task_id": str(task_id)})
                    else:
                        logger.warning("Task not found for status update", extra={"task_id": str(task_id)})
                    return updated
    
    def list_pending_tasks(self) -> List[TaskRecord]:
        """List all pending tasks."""
        with TracerContextManager.start_span("TaskRepository.list_pending_tasks"):
            logger.info("Listing pending tasks")
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, workflow_id, assignee_id, status, input_data, result, 
                               directives, parent_task_id, created_at, updated_at
                        FROM tasks
                        WHERE status = 'PENDING'
                        ORDER BY created_at ASC
                    """)
                    
                    tasks = []
                    for row in cur.fetchall():
                        task_record = TaskRecord(
                            id=row[0],
                            workflow_id=row[1],
                            assignee_id=row[2],
                            status=row[3],
                            input_data=row[4],
                            result=row[5],
                            directives=row[6],
                            parent_task_id=row[7],
                            created_at=row[8],
                            updated_at=row[9]
                        )
                        tasks.append(task_record)
                    
                    logger.info("Pending tasks retrieved", extra={"count": len(tasks)})
                    return tasks
    
    def find_tasks_by_result_property(self, key: str, value: Any) -> List[TaskRecord]:
        """Find tasks by a property in the result JSONB field."""
        with TracerContextManager.start_span("TaskRepository.find_tasks_by_result_property"):
            logger.info("Finding tasks by result property", extra={"key": key})
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    # Using JSONB containment operator to find tasks where result contains the key-value pair
                    cur.execute("""
                        SELECT id, workflow_id, assignee_id, status, input_data, result, 
                               directives, parent_task_id, created_at, updated_at
                        FROM tasks
                        WHERE result ->> %s = %s
                    """, (key, str(value)))
                    
                    tasks = []
                    for row in cur.fetchall():
                        task_record = TaskRecord(
                            id=row[0],
                            workflow_id=row[1],
                            assignee_id=row[2],
                            status=row[3],
                            input_data=row[4],
                            result=row[5],
                            directives=row[6],
                            parent_task_id=row[7],
                            created_at=row[8],
                            updated_at=row[9]
                        )
                        tasks.append(task_record)
                    
                    logger.info("Tasks found by result property", extra={"count": len(tasks), "key": key})
                    return tasks
    
    def update_task_context(self, task_id: UUID, context: Dict[str, Any]) -> bool:
        """Update task context (result field) without changing status."""
        with TracerContextManager.start_span("TaskRepository.update_task_context"):
            logger.info("Updating task context", extra={
                "task_id": str(task_id)
            })
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE tasks
                        SET result = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (json.dumps(context), str(task_id)))
                    
                    updated = cur.rowcount > 0
                    if updated:
                        logger.info("Task context updated successfully", extra={"task_id": str(task_id)})
                    else:
                        logger.warning("Task not found for context update", extra={"task_id": str(task_id)})
                    return updated
    
    def update_task_input_and_status(self, task_id: UUID, input_data: Dict[str, Any], status: str) -> bool:
        """Update task input data and status."""
        with TracerContextManager.start_span("TaskRepository.update_task_input_and_status"):
            logger.info("Updating task input data and status", extra={
                "task_id": str(task_id),
                "status": status
            })
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE tasks
                        SET input_data = %s, status = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (json.dumps(input_data), status, str(task_id)))
                    
                    updated = cur.rowcount > 0
                    if updated:
                        logger.info("Task input data and status updated successfully", extra={"task_id": str(task_id)})
                    else:
                        logger.warning("Task not found for input data and status update", extra={"task_id": str(task_id)})
                    return updated