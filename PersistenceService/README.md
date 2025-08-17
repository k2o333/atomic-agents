# PersistenceService Module

## Module Introduction
The PersistenceService is the database service module for the Synapse platform. It provides a unified interface for all database operations, including task and edge management, transaction handling, and versioning support.

## Module Functions
- Database connection pooling and management
- CRUD operations for tasks and edges
- Transaction management for business-level atomicity
- Task history/versioning support
- JSONB query support
- Integration with the Logging & Tracing Service

## Module Interface and How to Call

### Task Operations
```python
from PersistenceService.service import PersistenceService
from uuid import UUID

# Initialize the service
persistence_service = PersistenceService()

# Create a task
task_id = persistence_service.create_task(
    workflow_id=UUID('123e4567-e89b-12d3-a456-426614174000'),
    assignee_id="Agent:Worker",
    input_data={"goal": "Process user request"}
)

# Get a task
task = persistence_service.get_task(task_id)

# List pending tasks
pending_tasks = persistence_service.list_pending_tasks()

# Update task result
persistence_service.update_task_result(task_id, {"output": "Task completed"})

# Find tasks by result property
tasks = persistence_service.find_tasks_by_result_property("status", "success")
```

### Edge Operations
```python
# Get outgoing edges
edges = persistence_service.get_outgoing_edges(task_id)
```

### Workflow Operations
```python
from interfaces import PlanBlueprint, TaskDefinition, EdgeDefinition

# Create a workflow from a blueprint
blueprint = PlanBlueprint(
    workflow_id=UUID('123e4567-e89b-12d3-a456-426614174001'),
    new_tasks=[TaskDefinition(...)],
    new_edges=[EdgeDefinition(...)]
)
success = persistence_service.create_workflow_from_blueprint(blueprint)
```

### Task History Operations
```python
# Create a task history record
history_id = persistence_service.create_task_history_record(
    task_id=task_id,
    version_number=1,
    data_snapshot={"input": task.input_data, "result": {"output": "Task completed"}}
)

# Get task history records
history_records = persistence_service.get_task_history_by_task_id(task_id)

# Get latest task history record
latest_history = persistence_service.get_latest_task_history(task_id)
```

### Cleanup
```python
# Close the service
persistence_service.close()
```

## Parameters
- `workflow_id`: UUID of the workflow
- `assignee_id`: String identifier of the assignee (format: "Group:id" or "Agent:id")
- `input_data`: Dictionary containing task input data
- `task_id`: UUID of the task
- `result`: Dictionary containing task result data
- `parent_task_id`: UUID of the parent task (optional)
- `directives`: Dictionary containing task directives (optional)
- `source_task_id`: UUID of the source task for edges
- `target_task_id`: UUID of the target task for edges
- `condition`: Dictionary containing edge condition (optional)
- `data_flow`: Dictionary containing data flow mapping (optional)
- `version_number`: Integer version number for task history
- `data_snapshot`: Dictionary containing task data snapshot for history