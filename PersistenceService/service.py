"""
Persistence Service Main Interface

This module provides the main service interface for the Persistence Service,
implementing all public methods that other modules will use.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

# Import models from interfaces as required by the specification
from interfaces import PlanBlueprint, TaskDefinition, EdgeDefinition

from .config import DatabaseConfig
from .database import DatabaseManager
from .repository.task_repository import TaskRepository
from .repository.edge_repository import EdgeRepository
from .repository.task_history_repository import TaskHistoryRepository
from .transaction import TransactionManager
from .models.task import TaskRecord as DBTaskRecord, TaskHistoryRecord as DBTaskHistoryRecord
from .models.edge import EdgeRecord as DBEdgeRecord
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize logger
logger = get_logger(__name__)

class PersistenceService:
    """Main service class for the Persistence Service."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        self.config = config or DatabaseConfig()
        self.db_manager = DatabaseManager(self.config)
        self.task_repo = TaskRepository(self.db_manager)
        self.edge_repo = EdgeRepository(self.db_manager)
        self.task_history_repo = TaskHistoryRepository(self.db_manager)
        self.tx_manager = TransactionManager(self.db_manager)
    
    def create_task(self, workflow_id: UUID, assignee_id: str,
                   input_data: Optional[Dict[str, Any]] = None,
                   parent_task_id: Optional[UUID] = None,
                   directives: Optional[Dict[str, Any]] = None) -> UUID:
        """Create a new task and return its ID."""
        with TracerContextManager.start_span("PersistenceService.create_task"):
            logger.info("Creating task through service", extra={
                "workflow_id": str(workflow_id),
                "assignee_id": assignee_id
            })
            task_id = self.task_repo.create_task(workflow_id, assignee_id, input_data, parent_task_id, directives)
            logger.info("Task created through service", extra={"task_id": str(task_id)})
            return task_id
    
    def get_task(self, task_id: UUID) -> Optional[TaskDefinition]:
        """Get a task by its ID."""
        with TracerContextManager.start_span("PersistenceService.get_task"):
            logger.info("Getting task through service", extra={"task_id": str(task_id)})
            db_task = self.task_repo.get_task_by_id(task_id)
            if db_task:
                # Convert to interface model
                task_def = TaskDefinition(
                    task_id=str(db_task.id),
                    assignee_id=db_task.assignee_id,
                    input_data=db_task.input_data or {},
                    context_overrides=None,
                    directives=db_task.directives
                )
                logger.info("Task retrieved through service", extra={"task_id": str(task_id)})
                return task_def
            logger.info("Task not found through service", extra={"task_id": str(task_id)})
            return None
    
    def update_task_result(self, task_id: UUID, result: Dict[str, Any]) -> bool:
        """Update task result."""
        with TracerContextManager.start_span("PersistenceService.update_task_result"):
            logger.info("Updating task result through service", extra={"task_id": str(task_id)})
            updated = self.task_repo.update_task_status(task_id, "COMPLETED", result)
            logger.info("Task result updated through service", extra={"task_id": str(task_id), "updated": updated})
            return updated
    
    def update_task_status_and_result(self, task_id: UUID, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Update task status and optionally result."""
        with TracerContextManager.start_span("PersistenceService.update_task_status_and_result"):
            logger.info("Updating task status and result through service", extra={
                "task_id": str(task_id),
                "status": status
            })
            updated = self.task_repo.update_task_status(task_id, status, result)
            logger.info("Task status and result updated through service", extra={
                "task_id": str(task_id),
                "status": status,
                "updated": updated
            })
            return updated
    
    def list_pending_tasks(self) -> List[TaskDefinition]:
        """List all pending tasks."""
        with TracerContextManager.start_span("PersistenceService.list_pending_tasks"):
            logger.info("Listing pending tasks through service")
            db_tasks = self.task_repo.list_pending_tasks()
            task_defs = []
            for db_task in db_tasks:
                task_def = TaskDefinition(
                    task_id=str(db_task.id),
                    assignee_id=db_task.assignee_id,
                    input_data=db_task.input_data or {},
                    context_overrides=None,
                    directives=db_task.directives
                )
                task_defs.append(task_def)
            logger.info("Pending tasks listed through service", extra={"count": len(task_defs)})
            return task_defs
    
    def get_outgoing_edges(self, task_id: UUID) -> List[EdgeDefinition]:
        """Get outgoing edges for a task."""
        with TracerContextManager.start_span("PersistenceService.get_outgoing_edges"):
            logger.info("Getting outgoing edges through service", extra={"task_id": str(task_id)})
            db_edges = self.edge_repo.get_outgoing_edges(task_id)
            edge_defs = []
            for db_edge in db_edges:
                edge_def = EdgeDefinition(
                    source_task_id=str(db_edge.source_task_id),
                    target_task_id=str(db_edge.target_task_id),
                    condition=db_edge.condition,
                    data_flow=db_edge.data_flow
                )
                edge_defs.append(edge_def)
            logger.info("Outgoing edges retrieved through service", extra={"task_id": str(task_id), "count": len(edge_defs)})
            return edge_defs
    
    def create_workflow_from_blueprint(self, blueprint: PlanBlueprint) -> bool:
        """Create a workflow from a blueprint in a single transaction."""
        with TracerContextManager.start_span("PersistenceService.create_workflow_from_blueprint"):
            logger.info("Creating workflow from blueprint", extra={"workflow_id": str(blueprint.workflow_id)})
            
            try:
                with self.tx_manager.transaction() as conn:
                    # Create tasks
                    task_id_mapping = {}
                    for task_def in blueprint.new_tasks:
                        task_id = self.task_repo.create_task(
                            workflow_id=blueprint.workflow_id,
                            assignee_id=task_def.assignee_id,
                            input_data=task_def.input_data,
                            parent_task_id=UUID(task_def.parent_task_id) if task_def.parent_task_id else None,
                            directives=task_def.directives.dict() if task_def.directives else None
                        )
                        # Map the blueprint task ID to the actual task ID
                        task_id_mapping[task_def.task_id] = task_id
                    
                    # Create edges
                    for edge_def in blueprint.new_edges:
                        # Convert blueprint task IDs to actual task IDs
                        source_task_id = task_id_mapping.get(edge_def.source_task_id, edge_def.source_task_id)
                        target_task_id = task_id_mapping.get(edge_def.target_task_id, edge_def.target_task_id)
                        
                        # Convert to UUID if they are strings
                        if isinstance(source_task_id, str):
                            source_task_id = UUID(source_task_id)
                        if isinstance(target_task_id, str):
                            target_task_id = UUID(target_task_id)
                        
                        self.edge_repo.create_edge(
                            workflow_id=blueprint.workflow_id,
                            source_task_id=source_task_id,
                            target_task_id=target_task_id,
                            condition=edge_def.condition.dict() if edge_def.condition else None,
                            data_flow=edge_def.data_flow.dict() if edge_def.data_flow else None
                        )
                    
                    # Update tasks if needed
                    for task_update in blueprint.update_tasks:
                        if task_update.new_status or task_update.new_input_data:
                            # For simplicity, we're just updating status to a generic value
                            # In a real implementation, this would be more sophisticated
                            status = task_update.new_status or "UPDATED"
                            self.task_repo.update_task_status(
                                task_update.task_id, 
                                status, 
                                task_update.new_input_data
                            )
                
                logger.info("Workflow created successfully from blueprint", extra={"workflow_id": str(blueprint.workflow_id)})
                return True
            except Exception as e:
                logger.error("Failed to create workflow from blueprint", extra={
                    "workflow_id": str(blueprint.workflow_id),
                    "error": str(e)
                })
                return False
    
    def find_tasks_by_result_property(self, key: str, value: Any) -> List[TaskDefinition]:
        """Find tasks by a property in the result JSONB field."""
        with TracerContextManager.start_span("PersistenceService.find_tasks_by_result_property"):
            logger.info("Finding tasks by result property through service", extra={"key": key})
            db_tasks = self.task_repo.find_tasks_by_result_property(key, value)
            task_defs = []
            for db_task in db_tasks:
                task_def = TaskDefinition(
                    task_id=str(db_task.id),
                    assignee_id=db_task.assignee_id,
                    input_data=db_task.input_data or {},
                    context_overrides=None,
                    directives=db_task.directives
                )
                task_defs.append(task_def)
            logger.info("Tasks found by result property through service", extra={"count": len(task_defs), "key": key})
            return task_defs
    
    def update_task_context(self, task_id: UUID, context: Dict[str, Any]) -> bool:
        """Update task context (result field) without changing status."""
        with TracerContextManager.start_span("PersistenceService.update_task_context"):
            logger.info("Updating task context through service", extra={"task_id": str(task_id)})
            updated = self.task_repo.update_task_context(task_id, context)
            logger.info("Task context updated through service", extra={"task_id": str(task_id), "updated": updated})
            return updated
    
    def update_task_input_and_status(self, task_id: UUID, input_data: Dict[str, Any], status: str) -> bool:
        """Update task input data and status."""
        with TracerContextManager.start_span("PersistenceService.update_task_input_and_status"):
            logger.info("Updating task input data and status through service", extra={
                "task_id": str(task_id),
                "status": status
            })
            updated = self.task_repo.update_task_input_and_status(task_id, input_data, status)
            logger.info("Task input data and status updated through service", extra={
                "task_id": str(task_id),
                "status": status,
                "updated": updated
            })
            return updated
    
    def close(self) -> None:
        """Close all database connections."""
        with TracerContextManager.start_span("PersistenceService.close"):
            logger.info("Closing PersistenceService")
            self.db_manager.close_all_connections()
    
    def create_task_history_record(self, task_id: UUID, version_number: int, 
                                 data_snapshot: Dict[str, Any]) -> UUID:
        """Create a task history record."""
        with TracerContextManager.start_span("PersistenceService.create_task_history_record"):
            logger.info("Creating task history record through service", extra={
                "task_id": str(task_id),
                "version_number": version_number
            })
            history_id = self.task_history_repo.create_task_history_record(task_id, version_number, data_snapshot)
            logger.info("Task history record created through service", extra={"history_id": str(history_id)})
            return history_id
    
    def get_task_history_by_task_id(self, task_id: UUID) -> List[Dict[str, Any]]:
        """Get all history records for a task."""
        with TracerContextManager.start_span("PersistenceService.get_task_history_by_task_id"):
            logger.info("Getting task history records through service", extra={"task_id": str(task_id)})
            history_records = self.task_history_repo.get_task_history_by_task_id(task_id)
            
            # Convert to dictionary format for easier consumption
            result = []
            for record in history_records:
                result.append({
                    "id": str(record.id),
                    "task_id": str(record.task_id),
                    "version_number": record.version_number,
                    "data_snapshot": record.data_snapshot,
                    "created_at": record.created_at.isoformat() if hasattr(record.created_at, "isoformat") else str(record.created_at)
                })
            
            logger.info("Task history records retrieved through service", extra={"count": len(result)})
            return result
    
    def get_latest_task_history(self, task_id: UUID) -> Optional[Dict[str, Any]]:
        """Get the latest history record for a task."""
        with TracerContextManager.start_span("PersistenceService.get_latest_task_history"):
            logger.info("Getting latest task history record through service", extra={"task_id": str(task_id)})
            history_record = self.task_history_repo.get_latest_task_history(task_id)
            
            if history_record:
                result = {
                    "id": str(history_record.id),
                    "task_id": str(history_record.task_id),
                    "version_number": history_record.version_number,
                    "data_snapshot": history_record.data_snapshot,
                    "created_at": history_record.created_at.isoformat() if hasattr(history_record.created_at, "isoformat") else str(history_record.created_at)
                }
                logger.info("Latest task history record retrieved through service", extra={"history_id": str(history_record.id)})
                return result
            else:
                logger.info("No latest task history record found through service", extra={"task_id": str(task_id)})
                return None