# Central Graph Engine (Enhanced Event-Driven Version)

## Overview

The Central Graph Engine is the core orchestrator of the Synapse platform. It consumes tasks from a Redis queue using BRPOP, executes them by coordinating with other services, and manages the flow of complex workflows based on directives, intents, and edge conditions.

This enhanced version implements a full event-driven architecture using PostgreSQL triggers and a NOTIFY handler to eliminate polling.

## Features (Ultimate Version)

- Event-driven architecture using Redis BRPOP for task consumption
- Executes tasks assigned to Agents
- Handles `AgentResult` with `FinalAnswer` intent
- Handles `AgentResult` with `ToolCallRequest` intent (M2 enhancement)
- Handles `AgentResult` with `PlanBlueprint` intent (M3 enhancement)
- Updates task status in the database (`COMPLETED`, `FAILED`, or context updates)
- Evaluates Edge conditions using ConditionEvaluator
- Processes data flow mappings between tasks
- Basic logging and tracing integration

## Event-Driven Architecture

This enhanced version of the Central Graph Engine implements a full event-driven architecture:

1. **PostgreSQL Triggers**: Automatically send NOTIFY events when tasks are created or updated
2. **Notify Handler**: Listens for NOTIFY events and adds tasks to Redis queues
3. **Redis BRPOP**: Replaces polling with blocking queue consumption
4. **Real-time Processing**: Tasks are processed immediately when they become available

See `event_driven_architecture.md` for detailed implementation information.

## Dependencies

- `interfaces`: Core data models and interfaces
- `PersistenceService`: Database interaction
- `AgentService`: Agent execution
- `ToolService`: Tool execution
- `LoggingService`: Structured logging and tracing
- `simpleeval`: Safe expression evaluation for conditions
- `redis`: Redis client for task queue consumption

## Entry Point

The main entry point is the `main_loop()` function in `engine.py` (legacy version) or `engine_enhanced.py` (enhanced event-driven version), which starts the event-driven loop using Redis BRPOP.

```python
# Legacy version
from CentralGraphEngine.engine import main_loop

# Start the engine with default parameters
if __name__ == "__main__":
    main_loop()
```

```python
# Enhanced event-driven version
from CentralGraphEngine.engine_enhanced import main_loop

# Start the engine with default parameters
if __name__ == "__main__":
    main_loop()
```

## Configuration

The engine can be configured with custom Redis connection parameters:

```python
main_loop(redis_host='redis.example.com', redis_port=6380, task_queue='synapse_tasks')
```