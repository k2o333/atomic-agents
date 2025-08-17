"""
Edge Model for Persistence Service

This module defines the data models for edges that map to the edges table.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from uuid import UUID
from datetime import datetime

@dataclass
class EdgeRecord:
    """Data class representing an edge record in the database."""
    id: UUID
    workflow_id: UUID
    source_task_id: UUID
    target_task_id: UUID
    condition: Optional[Dict[str, Any]]
    data_flow: Optional[Dict[str, Any]]
    created_at: datetime