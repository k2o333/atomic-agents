"""
Edge Repository for Persistence Service

This module provides data access methods for edges.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import logging

from ..models.edge import EdgeRecord
from ..database import DatabaseManager
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize logger
logger = get_logger(__name__)

class EdgeRepository:
    """Repository class for edge-related database operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def get_outgoing_edges(self, task_id: UUID) -> List[EdgeRecord]:
        """Get all edges that originate from the specified task."""
        with TracerContextManager.start_span("EdgeRepository.get_outgoing_edges"):
            logger.info("Fetching outgoing edges", extra={"source_task_id": str(task_id)})
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, workflow_id, source_task_id, target_task_id, condition, data_flow, created_at
                        FROM edges
                        WHERE source_task_id = %s
                        ORDER BY created_at ASC
                    """, (task_id,))
                    
                    edges = []
                    for row in cur.fetchall():
                        edge_record = EdgeRecord(
                            id=row[0],
                            workflow_id=row[1],
                            source_task_id=row[2],
                            target_task_id=row[3],
                            condition=row[4],
                            data_flow=row[5],
                            created_at=row[6]
                        )
                        edges.append(edge_record)
                    
                    logger.info("Outgoing edges retrieved", extra={"count": len(edges)})
                    return edges
    
    def create_edge(self, workflow_id: UUID, source_task_id: UUID, 
                   target_task_id: UUID, condition: Optional[Dict[str, Any]] = None,
                   data_flow: Optional[Dict[str, Any]] = None) -> UUID:
        """Create a new edge and return its ID."""
        with TracerContextManager.start_span("EdgeRepository.create_edge"):
            logger.info("Creating new edge", extra={
                "workflow_id": str(workflow_id),
                "source_task_id": str(source_task_id),
                "target_task_id": str(target_task_id)
            })
            
            with self.db_manager.get_db_session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO edges (workflow_id, source_task_id, target_task_id, condition, data_flow)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (workflow_id, source_task_id, target_task_id, 
                          json.dumps(condition) if condition else None,
                          json.dumps(data_flow) if data_flow else None))
                    
                    edge_id = cur.fetchone()[0]
                    logger.info("Edge created successfully", extra={"edge_id": str(edge_id)})
                    return edge_id