# Central Graph Engine

## Overview

The Central Graph Engine is the core orchestrator of the Synapse platform. It consumes tasks from a queue, executes them by coordinating with other services, and manages the flow of a workflow based on the directives and intents returned.

## Features (Current)

- Polls the database for pending tasks (`PENDING` status)
- Executes tasks assigned to Agents
- Handles `AgentResult` with `FinalAnswer` intent
- Handles `AgentResult` with `ToolCallRequest` intent (M2 enhancement)
- Updates task status in the database (`COMPLETED`, `FAILED`, or context updates)
- Basic logging and tracing integration

## ToolCallRequest Handling (M2 Enhancement)

When an Agent returns a `ToolCallRequest` intent:
1. The engine calls `ToolService.run_tool()` to execute the requested tool
2. Gets the tool execution result
3. Updates the task's context (result field) with the tool result using `PersistenceService.update_task_context()`
4. Does NOT mark the task as `COMPLETED` - it remains `PENDING`
5. The database `UPDATE` operation automatically triggers `NOTIFY`, causing the same `task_id` to be re-queued for agent re-entry

This enables the "think-act" cycle where an Agent can call tools and then re-enter with the tool results.

## Future Enhancements (M3)

The following features will be implemented in later milestones:

- Handling `PlanBlueprint` intents
- Task directives processing (loop, timeout, etc.)
- Event-driven architecture using Redis BRPOP/LISTEN-NOTIFY
- Condition evaluation for task edges
- Complex workflow orchestration

## Dependencies

- `interfaces`: Core data models and interfaces
- `PersistenceService`: Database interaction
- `AgentService`: Agent execution
- `ToolService`: Tool execution
- `LoggingService`: Structured logging and tracing

## Entry Point

The main entry point is the `main_loop()` function in `engine.py`, which starts the polling loop.