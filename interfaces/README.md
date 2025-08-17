# /root/projects/atom_agents/interfaces/README.md

## Interface Module

This module defines the core data contracts for the Synapse platform using Pydantic models. It serves as the single source of truth for data structures exchanged between different system components.

### Module Introduction

The interfaces module provides a standardized set of Pydantic models that define the data contracts used throughout the Synapse platform. These models ensure type safety, data validation, and consistent communication between all system components.

### Module Functionality

- **Data Validation**: All models use Pydantic v2 for automatic data validation and type checking
- **Structured Logging**: Integrated with LoggingService for automatic initialization logging
- **Distributed Tracing**: Automatic trace span creation for all model instantiations
- **Extensibility**: Designed with future growth in mind using Union types and nested models

### Key Models

#### PlanBlueprint
Used for defining and extending workflows declaratively.
- `workflow_id`: Optional UUID identifying the workflow
- `new_tasks`: List of TaskDefinition objects to be created
- `new_edges`: List of EdgeDefinition objects connecting tasks
- `update_tasks`: List of TaskUpdate objects for modifying existing tasks

#### AgentResult
Standardized output from all Agent executions.
- `status`: Either 'SUCCESS' or 'FAILURE'
- `output`: AgentIntent containing the agent's thought and intent
- `failure_details`: Optional FailureDetails for error cases
- `metadata`: Optional dictionary for additional information

#### ContextBuildConfig
Defines what context an Agent requires for execution.
- `task_id`: UUID of the task requiring context
- `include_metadata`: Boolean flag for including metadata
- `include_tool_list`: Boolean flag for including tool list
- Various configuration options for different context components

#### TaskDirectives
Instructions for the graph engine (e.g., loops, timeouts, failure handling).
- `loop_directive`: Optional LoopDirective for iteration patterns
- `on_failure`: Configuration for failure handling
- `timeout_seconds`: Optional timeout setting
- `human_interaction`: Configuration for human intervention

#### InterventionRequest
For human intervention in workflows.
- `intervention_type`: Type of intervention (PAUSE, RESUME, ROLLBACK_AND_MODIFY)
- `target_task_id`: UUID of the task to intervene on
- Various fields for rollback and modification operations

### Module Interface Usage

To use these models in other parts of the system:

```python
from interfaces import PlanBlueprint, AgentResult, ContextBuildConfig, TaskDirectives, InterventionRequest
```

#### PlanBlueprint Usage
```python
from interfaces import PlanBlueprint, TaskDefinition

# Create a new task
task = TaskDefinition(
    task_id="task_1",
    input_data={"goal": "Process user request"},
    assignee_id="Agent:Worker"
)

# Create a blueprint with the task
blueprint = PlanBlueprint(
    workflow_id="123e4567-e89b-12d3-a456-426614174000",
    new_tasks=[task]
)
```

#### AgentResult Usage
```python
from interfaces import AgentResult, AgentIntent, FinalAnswer

# Create a successful result
result = AgentResult(
    status="SUCCESS",
    output=AgentIntent(
        thought="Task completed successfully",
        intent=FinalAnswer(content="Final result here")
    )
)
```

#### ContextBuildConfig Usage
```python
import uuid
from interfaces import ContextBuildConfig

# Request context for a task
config = ContextBuildConfig(
    task_id=uuid.uuid4(),
    include_metadata=True,
    conversation_history_config={"last_n": 5}
)
```

### Logging and Tracing

This module is integrated with the LoggingService to provide structured logging and distributed tracing capabilities. All model initializations are automatically traced and logged when the LoggingService is available.

To use logging and tracing in your modules:

1. Ensure LoggingService is properly installed and configured
2. Import the models as usual - logging is automatically enabled
3. The models will automatically create trace spans and log their initialization

Example usage with tracing:
```python
from LoggingService.sdk import TracerContextManager
from interfaces import PlanBlueprint

# Start a new trace
with TracerContextManager.start_trace("my_workflow"):
    # Create a model instance (automatically traced)
    blueprint = PlanBlueprint(workflow_id="123e4567-e89b-12d3-a456-426614174000")
```

### Testing

Tests are written using the built-in `unittest` framework and cover all major functionality.

To run the basic tests:
```bash
cd /root/projects/atom_agents
/root/projects/atom_agents/myenv311/bin/python -m unittest interfaces/tests/test_interfaces.py
```

To run the comprehensive tests (covering all test cases from test.md):
```bash
cd /root/projects/atom_agents
/root/projects/atom_agents/myenv311/bin/python -m unittest interfaces/tests/test_interfaces_comprehensive.py
```

All tests should pass successfully, verifying that:
1. All model structures are correctly implemented
2. Data validation works as expected
3. Logging and tracing integration functions properly
4. All edge cases are handled appropriately

### Test Coverage

The comprehensive test suite covers:
- Basic model structure validation
- Nested model instantiation
- Field validation and type checking
- Special cases like loops and failure handling
- Logging and tracing functionality
- All specific test cases documented in test.md