#!/usr/bin/env python3
"""
Central Graph Engine (M1 Polling Validation Version)

This is the core orchestrator of the Synapse platform. It consumes tasks from a queue,
executes them by coordinating with other services, and manages the flow of a workflow
based on the directives and intents returned.

For M1, this implements a polling model for validation purposes before moving to PostgreSQL NOTIFY.
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from uuid import UUID

# Import core interfaces
from interfaces import (
    TaskDefinition, EdgeDefinition, AgentResult, ToolCallRequest, FinalAnswer, PlanBlueprint,
    TaskDirectives, LoopDirective
)

# Import service interfaces (these would be actual service clients in a real implementation)
# For M1, we'll use mock services or placeholders
try:
    from PersistenceService.service import PersistenceService
    persistence_service = PersistenceService()
except ImportError:
    # Fallback mock for M1
    class MockPersistenceService:
        def list_pending_tasks(self):
            # For demo, return an empty list
            return []
        
        def update_task_status(self, task_id, status, result=None):
            print(f"[MockPersistence] Task {task_id} status updated to {status}")
            
        def get_outgoing_edges(self, task_id):
            # For demo, return an empty list
            return []
            
        def create_workflow_from_blueprint(self, blueprint: PlanBlueprint):
            print(f"[MockPersistence] Creating workflow from blueprint with {len(blueprint.new_tasks)} tasks.")
            return True
            
    persistence_service = MockPersistenceService()

try:
    from AgentService.service import AgentService
    agent_service = AgentService()
except ImportError:
    class MockAgentService:
        def execute_agent(self, task: TaskDefinition):
            # For demo, return a mock final answer
            print(f"[MockAgent] Executing agent {task.assignee_id}")
            return AgentResult(
                status="SUCCESS",
                output={
                    "thought": "This is a mock response for M1.",
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
            # Return a mock ToolResult
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

def handle_completed_task(task: TaskDefinition) -> None:
    """
    Handle a completed task by evaluating downstream edges.
    
    This is an M2+ feature placeholder for now.
    
    Args:
        task: The completed task
    """
    with TracerContextManager.start_span(f"handle_completed_task_{task.task_id}") as span:
        logger.info(f"Handling completed task {task.task_id}")
        try:
            # M2+ functionality: Find and evaluate downstream edges
            edges = persistence_service.get_outgoing_edges(task.task_id)
            logger.info(f"Found {len(edges)} outgoing edges for task {task.task_id}")
            
            # For M1, we'll just log the edges but not process them
            for edge in edges:
                logger.info(f"Found edge from {edge.source_task_id} to {edge.target_task_id}")
                # Future M2+: evaluate_condition and trigger next tasks
        except Exception as e:
            logger.exception(f"Error handling completed task {task.task_id}")

def process_task(task: TaskDefinition) -> None:
    """
    Process a single task. This is the core execution logic for M1.
    
    In M1, we only handle:
    1. Tasks assigned to Agents
    2. Agent returning FinalAnswer
    
    Future enhancements will handle:
    - ToolCallRequest intents
    - PlanBlueprint intents
    - Task directives (loop, timeout, etc.)
    """
    with TracerContextManager.start_span(f"process_task_{task.task_id}") as span:
        logger.info(f"Starting to process task {task.task_id}", extra={
            "task_id": task.task_id,
            "assignee_id": task.assignee_id
        })
        
        try:
            # 1. Check if the assignee is an Agent (for M1, we only handle agents)
            if task.assignee_id.startswith("Agent:"):
                # 2. Execute the agent
                agent_result: AgentResult = agent_service.execute_agent(task)
                
                logger.info(f"Agent {task.assignee_id} executed", extra={
                    "task_id": task.task_id,
                    "agent_result_status": agent_result.status
                })
                
                # 3. Handle the agent's intent
                if agent_result.status == "SUCCESS":
                    intent = agent_result.output.intent
                    
                    # M1: Handle FinalAnswer
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
                    
                    # M2: Handle ToolCallRequest
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
                    
                    # Future M3: Handle PlanBlueprint
                    # elif isinstance(intent, PlanBlueprint):
                    #     # Create new tasks and edges from the blueprint
                    #     persistence_service.create_workflow_from_blueprint(intent)
                    #     # Mark original task as COMPLETED
                    #     persistence_service.update_task_status_and_result(
                    #         task_id=uuid.UUID(task.task_id),
                    #         status="COMPLETED",
                    #         result={"message": "Plan executed successfully"}
                    #     )
                
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

def evaluate_condition(condition: Optional[Dict[str, Any]], task_result: Dict[str, Any]) -> bool:
    """
    Evaluate a condition (e.g., from an Edge) based on the previous task's result.
    
    For M1, this is a placeholder. In M3, we'll implement a real CEL evaluator.
    """
    # M1: Always return True to keep the flow simple
    return True

def process_directives(directives: Optional[TaskDirectives], task_id: str) -> bool:
    """
    Process task directives like loop, timeout, etc.
    
    For M1, this is a placeholder. We'll implement real logic in later milestones.
    """
    if directives:
        logger.info(f"Processing directives for task {task_id}", extra={"directives": directives.dict()})
        # M1: Log the directives but don't act on them
        if directives.loop_directive:
            logger.info("Loop directive detected (M1: not implemented)", extra={
                "loop_type": directives.loop_directive.type
            })
        if directives.timeout_seconds:
            logger.info("Timeout directive detected (M1: not implemented)", extra={
                "timeout_seconds": directives.timeout_seconds
            })
    return True

def main_loop(polling_interval: int = 5) -> None:
    """
    Main execution loop for the Central Graph Engine.
    
    In M1, this implements a polling model for validation purposes before moving to PostgreSQL NOTIFY.
    The engine polls the PersistenceService for pending tasks.
    
    Args:
        polling_interval: The interval in seconds between polling attempts
    """
    logger.info("Central Graph Engine (M1 Polling Validation) started", extra={
        "polling_interval": polling_interval
    })
    
    with TracerContextManager.start_trace("central_graph_engine_main_loop"):
        while True:
            try:
                # 1. Poll for pending tasks
                logger.info("Polling for pending tasks...")
                pending_tasks = persistence_service.list_pending_tasks()
                
                if not pending_tasks:
                    logger.info("No pending tasks found. Sleeping...", extra={"interval": polling_interval})
                    time.sleep(polling_interval)
                    continue
                
                logger.info(f"Found {len(pending_tasks)} pending tasks")
                
                # 2. Process each task
                for task_def in pending_tasks:
                    with TracerContextManager.start_span(f"process_task_{task_def.task_id}") as span:
                        # For M1 validation, we'll process the task directly without locking
                        # In the final implementation, we'll use get_task_and_lock
                        process_task(task_def)
                        
            except KeyboardInterrupt:
                logger.info("Received interrupt signal. Shutting down...")
                break
            except Exception as e:
                logger.exception("Unexpected error in main loop")
                # In a production system, we might want to implement a backoff strategy
                # For now, we'll just continue to avoid tight loop on persistent errors
                time.sleep(polling_interval)

if __name__ == "__main__":
    main_loop()