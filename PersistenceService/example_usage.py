"""
Example usage of the PersistenceService

This script demonstrates how to use the PersistenceService module.
"""

from uuid import UUID
from PersistenceService.service import PersistenceService

def main():
    """Example usage of the PersistenceService."""
    # Initialize the service
    persistence_service = PersistenceService()
    
    print("PersistenceService initialized successfully!")
    
    # Create a task
    workflow_id = UUID('123e4567-e89b-12d3-a456-426614174000')
    task_id = persistence_service.create_task(
        workflow_id=workflow_id,
        assignee_id="Agent:Worker",
        input_data={"goal": "Process user request", "data": {"key": "value"}}
    )
    print(f"Created task with ID: {task_id}")
    
    # Get the task
    task = persistence_service.get_task(task_id)
    if task:
        print(f"Retrieved task: {task.task_id} assigned to {task.assignee_id}")
    else:
        print("Task not found")
    
    # List pending tasks
    pending_tasks = persistence_service.list_pending_tasks()
    print(f"Found {len(pending_tasks)} pending tasks")
    
    # Update task result
    result_updated = persistence_service.update_task_result(
        task_id, 
        {"output": "Task completed successfully", "status": "success"}
    )
    print(f"Task result updated: {result_updated}")
    
    # Create an edge
    edge_id = persistence_service.edge_repo.create_edge(
        workflow_id=workflow_id,
        source_task_id=task_id,
        target_task_id=UUID('123e4567-e89b-12d3-a456-426614174001'),
        condition={"evaluator": "CEL", "expression": "result.status == 'success'"}
    )
    print(f"Created edge with ID: {edge_id}")
    
    # Get outgoing edges
    edges = persistence_service.get_outgoing_edges(task_id)
    print(f"Found {len(edges)} outgoing edges")
    
    # Find tasks by result property
    tasks_by_result = persistence_service.find_tasks_by_result_property("status", "success")
    print(f"Found {len(tasks_by_result)} tasks with status 'success'")
    
    # Create a task history record
    history_id = persistence_service.create_task_history_record(
        task_id=task_id,
        version_number=1,
        data_snapshot={"input": task.input_data, "result": {"output": "Task completed successfully"}}
    )
    print(f"Created task history record with ID: {history_id}")
    
    # Get task history records
    history_records = persistence_service.get_task_history_by_task_id(task_id)
    print(f"Found {len(history_records)} history records for task")
    
    # Get latest task history record
    latest_history = persistence_service.get_latest_task_history(task_id)
    if latest_history:
        print(f"Latest history record version: {latest_history['version_number']}")
    else:
        print("No history records found")
    
    # Clean up
    persistence_service.close()
    print("PersistenceService closed successfully!")

if __name__ == "__main__":
    main()