"""
Task Model for Persistence Service

This module defines the data models for tasks that map to the tasks table.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class TaskRecord:
    """Data class representing a task record in the database."""
    id: UUID
    workflow_id: UUID
    assignee_id: str
    status: str
    input_data: Optional[Dict[str, Any]]
    result: Optional[Dict[str, Any]]
    directives: Optional[Dict[str, Any]]
    parent_task_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

@dataclass
class TaskHistoryRecord:
    """Data class representing a task history record."""
    id: UUID
    task_id: UUID
    version_number: int
    data_snapshot: Dict[str, Any]
    created_at: datetime