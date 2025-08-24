#!/usr/bin/env python3
"""
Enhanced Central Graph Engine with Redis BRPOP loop

This is the enhanced version of the Central Graph Engine that implements
the event-driven model using Redis BRPOP to consume tasks from a queue.
"""

import time
import uuid
from typing import Dict, Any, Optional, List
import redis
import logging

# Import core interfaces
from interfaces import (
    TaskDefinition, EdgeDefinition, AgentResult, ToolCallRequest, FinalAnswer, PlanBlueprint,
    TaskDirectives, LoopDirective, DataFlow
)

# Import ConditionEvaluator
from .condition_evaluator import condition_evaluator

# Import service interfaces
try:
    from PersistenceService.service import PersistenceService
    persistence_service = PersistenceService()
except ImportError:
    # Fallback mock for development
    class MockPersistenceService:
        def list_pending_tasks(self):
            return []
        
        def update_task_status(self, task_id, status, result=None):
            print(f"[MockPersistence] Task {task_id} status updated to {status}")
            
        def get_outgoing_edges(self, task_id):
            return []
            
        def create_workflow_from_blueprint(self, blueprint: PlanBlueprint):
            print(f"[MockPersistence] Creating workflow from blueprint with {len(blueprint.new_tasks)} tasks.")
            return True
            
        def get_task_and_lock(self, task_id: str):
            # Mock implementation
            return TaskDefinition(
                task_id=task_id,
                assignee_id="Agent:Worker",
                input_data={},
                context_overrides=None,
                directives=None
            )
            
    persistence_service = MockPersistenceService()

try:
    from AgentService.service import AgentService
    agent_service = AgentService()
except ImportError:
    class MockAgentService:
        def execute_agent(self, task: TaskDefinition):
            print(f"[MockAgent] Executing agent {task.assignee_id}")
            return AgentResult(
                status="SUCCESS",
                output={
                    "thought": "This is a mock response.",
                    "intent": FinalAnswer(content="Hello World from Mock Agent!")
                }
            )
    agent_service = MockAgentService()

try:
    from toolservices.service import ToolService
    tool_service = ToolService()
except ImportError:
    class MockToolService:
        def run_tool(self, tool_call: ToolCallRequest):
            print(f"[MockTool] Executing tool {tool_call.tool_id} with args {tool_call.arguments}")
            from interfaces import ToolResult
            return ToolResult(
                status="SUCCESS",
                output=f"Mock result for {tool_call.tool_id}"
            )
    tool_service = MockToolService()

# Import logging and tracing
try:
    from LoggingService.sdk import get_logger, TracerContextManager
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    class TracerContextManager:
        @staticmethod
        def start_trace(name: str):
            from contextlib import nullcontext
            return nullcontext()
        
        @staticmethod
        def start_span(name: str):
            from contextlib import nullcontext
            return nullcontext()


def get_task_and_lock(task_id: str) -> Optional[TaskDefinition]:
    """
    Get a task and lock it for processing.
    
    This method uses SELECT ... FOR UPDATE SKIP LOCKED to atomically
    get the task and lock the row, preventing other engine instances
    from processing the same task.
    
    Args:
        task_id: The ID of the task to get and lock
        
    Returns:
        TaskDefinition if successfully locked, None otherwise
    """
    with TracerContextManager.start_span(f"get_task_and_lock_{task_id}") as span:
        logger.info(f"Attempting to get and lock task {task_id}")
        try:
            # Call the persistence service to get and lock the task
            task = persistence_service.get_task_and_lock(task_id)
            if task:
                logger.info(f"Successfully locked task {task_id}")
                return task
            else:
                logger.info(f"Task {task_id} is already locked by another instance")
                return None
        except Exception as e:
            logger.exception(f"Error getting and locking task {task_id}")
            return None


def apply_data_flow(data_flow: Optional[DataFlow], source_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply data flow mapping to transform source task result into target task input.
    
    Args:
        data_flow: The data flow definition with mappings
        source_result: The result from the source task
        
    Returns:
        Dict[str, Any]: Transformed input data for the target task
    """
    if not data_flow or not data_flow.mappings:
        # If no data flow is defined, return empty dict
        return {}
    
    target_input = {}
    for target_key, source_expr in data_flow.mappings.items():
        try:
            # For simplicity, we'll assume the source_expr is a direct key reference
            # In a more advanced implementation, this could be a CEL expression
            if source_expr in source_result:
                target_input[target_key] = source_result[source_expr]
            else:
                # If the expression is not a direct key, treat it as a literal value
                target_input[target_key] = source_expr
        except Exception as e:
            logger.warning(f"Error applying data flow mapping {target_key} -> {source_expr}: {str(e)}")
            # Default to the expression itself as a literal value
            target_input[target_key] = source_expr
    
    return target_input


def handle_completed_task(task: TaskDefinition) -> None:
    """
    Handle a completed task by evaluating downstream edges and activating correct downstream tasks.
    
    This implements the ultimate Edge condition routing functionality.
    
    Args:
        task: The completed task
    """
    with TracerContextManager.start_span(f"handle_completed_task_{task.task_id}") as span:
        logger.info(f"Handling completed task {task.task_id}")
        try:
            # Get the task result from the database
            db_task = persistence_service.task_repo.get_task_by_id(uuid.UUID(task.task_id))
            task_result = db_task.result if db_task and db_task.result else {}
            
            # Find and evaluate downstream edges
            edges = persistence_service.get_outgoing_edges(uuid.UUID(task.task_id))
            logger.info(f"Found {len(edges)} outgoing edges for task {task.task_id}")
            
            # Process each edge
            for edge in edges:
                logger.info(f"Processing edge from {edge.source_task_id} to {edge.target_task_id}")
                
                # Evaluate the edge condition
                condition_result = condition_evaluator.evaluate(edge.condition, task_result)
                logger.info(f"Condition evaluation for edge {edge.source_task_id}->{edge.target_task_id}: {condition_result}")
                
                # If condition is satisfied, activate the target task
                if condition_result:
                    logger.info(f"Activating downstream task {edge.target_task_id}")
                    
                    # Apply data flow mapping if defined
                    input_data = apply_data_flow(edge.data_flow, task_result)
                    logger.info(f"Applied data flow, input data for task {edge.target_task_id}: {input_data}")
                    
                    # Update the target task with the mapped input data
                    try:
                        # Update target task with mapped input data and set status to PENDING
                        persistence_service.update_task_input_and_status(
                            task_id=uuid.UUID(edge.target_task_id),
                            input_data=input_data,
                            status="PENDING"
                        )
                        logger.info(f"Successfully activated downstream task {edge.target_task_id}")
                    except Exception as e:
                        logger.error(f"Failed to activate downstream task {edge.target_task_id}: {str(e)}")
                    
        except Exception as e:
            logger.exception(f"Error handling completed task {task.task_id}")


def process_task(task: TaskDefinition) -> None:
    """
    Process a single task. This is the core execution logic.
    
    Handles:
    1. Tasks assigned to Agents
    2. Agent returning FinalAnswer
    3. Agent returning ToolCallRequest
    4. Agent returning PlanBlueprint
    5. Task directives (loop, timeout, etc.)
    """
    with TracerContextManager.start_span(f"process_task_{task.task_id}") as span:
        logger.info(f"Starting to process task {task.task_id}", extra={
            "task_id": task.task_id,
            "assignee_id": task.assignee_id
        })
        
        try:
            # Process task directives first
            if task.directives:
                process_directives(task.directives, task.task_id)
            
            # Check if the assignee is an Agent
            if task.assignee_id.startswith("Agent:"):
                # Execute the agent
                agent_result: AgentResult = agent_service.execute_agent(task)
                
                logger.info(f"Agent {task.assignee_id} executed", extra={
                    "task_id": task.task_id,
                    "agent_result_status": agent_result.status
                })
                
                # Handle the agent's intent
                if agent_result.status == "SUCCESS":
                    intent = agent_result.output.intent
                    
                    # Handle FinalAnswer
                    if isinstance(intent, FinalAnswer):
                        # Update task status to COMPLETED with the result
                        persistence_service.update_task_status_and_result(
                            task_id=uuid.UUID(task.task_id),
                            status="COMPLETED",
                            result={"content": intent.content}
                        )
                        logger.info(f"Task {task.task_id} completed with final answer", extra={
                            "content": intent.content
                        })
                    
                    # Handle ToolCallRequest
                    elif isinstance(intent, ToolCallRequest):
                        # Execute the tool and get result
                        tool_result = tool_service.run_tool(intent)
                        
                        # Update task context with tool result for agent re-entry
                        # Do NOT mark task as COMPLETED - it will be re-queued for re-entry
                        context_update = {"last_tool_result": tool_result.dict() if hasattr(tool_result, 'dict') else tool_result}
                        persistence_service.update_task_context(
                            task_id=uuid.UUID(task.task_id),
                            context=context_update
                        )
                        logger.info(f"Task {task.task_id} updated with tool result for re-entry", extra={
                            "tool_id": intent.tool_id,
                            "tool_result": tool_result.dict() if hasattr(tool_result, 'dict') else tool_result
                        })
                        # Note: The database UPDATE will automatically trigger NOTIFY,
                        # which will cause the task to be re-queued for re-entry
                    
                    # Handle PlanBlueprint
                    elif isinstance(intent, PlanBlueprint):
                        # Create new tasks and edges from the blueprint
                        success = persistence_service.create_workflow_from_blueprint(intent)
                        # Mark original task as COMPLETED
                        persistence_service.update_task_status_and_result(
                            task_id=uuid.UUID(task.task_id),
                            status="COMPLETED",
                            result={"message": "Plan executed successfully"}
                        )
                        if success:
                            logger.info(f"PlanBlueprint processed successfully for task {task.task_id}")
                        else:
                            logger.error(f"Failed to process PlanBlueprint for task {task.task_id}")
                
                elif agent_result.status == "FAILURE":
                    # Handle failure
                    persistence_service.update_task_status_and_result(
                        task_id=uuid.UUID(task.task_id),
                        status="FAILED",
                        result={
                            "failure_details": agent_result.failure_details.dict() if agent_result.failure_details else None,
                            "thought": agent_result.output.thought if agent_result.output else ""
                        }
                    )
                    logger.error(f"Agent {task.assignee_id} failed", extra={
                        "task_id": task.task_id,
                        "failure_details": agent_result.failure_details.dict() if agent_result.failure_details else None
                    })
            
            # Future: Handle tasks assigned to Tools, Groups, etc.
            # elif task.assignee_id.startswith("Tool:"):
            #     ...
            # elif task.assignee_id.startswith("Group:"):
            #     ...
            
        except Exception as e:
            logger.exception(f"Error processing task {task.task_id}", extra={"task_id": task.task_id})
            # Mark task as failed in case of unexpected error
            persistence_service.update_task_status_and_result(
                task_id=uuid.UUID(task.task_id),
                status="FAILED",
                result={"error": str(e)}
            )


def process_directives(directives: Optional[TaskDirectives], task_id: str) -> bool:
    """
    Process task directives like loop, timeout, etc.
    """
    if directives:
        logger.info(f"Processing directives for task {task_id}", extra={"directives": directives.dict()})
        # Log the directives but don't act on them in this implementation
        if directives.loop_directive:
            logger.info("Loop directive detected", extra={
                "loop_type": directives.loop_directive.type
            })
        if directives.timeout_seconds:
            logger.info("Timeout directive detected", extra={
                "timeout_seconds": directives.timeout_seconds
            })
    return True


def main_loop(redis_host: str = 'localhost', redis_port: int = 6379, task_queue: str = 'task_execution_queue') -> None:
    """
    Main execution loop for the Central Graph Engine (Enhanced Version).
    
    This implements the event-driven model using Redis BRPOP to consume tasks from a queue.
    
    Args:
        redis_host: Redis server hostname
        redis_port: Redis server port
        task_queue: Name of the Redis list used as task queue
    """
    logger.info("Central Graph Engine (Enhanced Version) started", extra={
        "redis_host": redis_host,
        "redis_port": redis_port,
        "task_queue": task_queue
    })
    
    # Import redis client
    try:
        redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        logger.info("Connected to Redis successfully")
    except ImportError:
        logger.error("Redis library not available. Please install redis: pip install redis")
        return
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        return
    
    with TracerContextManager.start_trace("central_graph_engine_main_loop"):
        while True:
            try:
                # Blockingly wait for a task from Redis queue
                logger.info("Waiting for tasks from Redis queue...")
                result = redis_client.brpop(task_queue, timeout=0)  # Block indefinitely
                
                if result is None:
                    # Timeout occurred, continue waiting
                    continue
                    
                # Extract task_id from the result
                queue_name, task_id = result
                logger.info(f"Received task from queue: {task_id}")
                
                # Get and lock the task
                task = get_task_and_lock(task_id)
                if task is None:
                    # Task is already being processed by another instance
                    logger.info(f"Task {task_id} is already locked, skipping")
                    continue
                
                # Process the task based on its status
                if task.status == "COMPLETED":
                    # Handle completed task by evaluating downstream edges
                    handle_completed_task(task)
                elif task.status == "PENDING":
                    # Process pending task (assigned to an Agent)
                    process_task(task)
                else:
                    logger.warning(f"Unknown task status for task {task_id}: {task.status}")
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal. Shutting down...")
                break
            except Exception as e:
                logger.exception("Unexpected error in main loop")
                # Continue to avoid tight loop on persistent errors
                continue


if __name__ == "__main__":
    main_loop()