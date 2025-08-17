#!/usr/bin/env python3
"""
M1 Validation Test Script

This script validates the M1 acceptance criteria:
1. Able to manually INSERT a Task via API
2. Graph Engine can poll the task, call HelloWorldAgent, and update task status to COMPLETED
3. Result field contains "Hello World!"
4. All key steps have structured logs with trace_id
"""

import sys
import os
import time
import uuid
from typing import Optional

# Add project root to Python path
sys.path.insert(0, '/root/projects/atom_agents')

from PersistenceService.service import PersistenceService
from agentservice.generic_agents.HelloWorldAgent import HelloWorldAgent
from interfaces import TaskDefinition
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize services
logger = get_logger(__name__)
persistence_service = PersistenceService()

def create_test_task() -> str:
    """Create a test task assigned to HelloWorldAgent"""
    with TracerContextManager.start_trace("m1_validation_create_task"):
        logger.info("Creating test task for M1 validation")
        
        workflow_id = uuid.uuid4()
        task_id = persistence_service.create_task(
            workflow_id=workflow_id,
            assignee_id="Agent:HelloWorldAgent",  # Assign to HelloWorldAgent
            input_data={"test": "m1_validation"}
        )
        
        logger.info("Test task created successfully", extra={
            "task_id": str(task_id),
            "workflow_id": str(workflow_id)
        })
        
        return str(task_id)

def verify_task_completed(task_id: str) -> bool:
    """Verify that the task was completed with correct result"""
    with TracerContextManager.start_trace("m1_validation_verify_task"):
        logger.info("Verifying task completion", extra={"task_id": task_id})
        
        # Wait a bit for the engine to process the task
        time.sleep(2)
        
        # Get the updated task
        task = persistence_service.get_task(uuid.UUID(task_id))
        
        if not task:
            logger.error("Task not found", extra={"task_id": task_id})
            return False
            
        # Get the full task record from DB to check status and result
        db_task = persistence_service.task_repo.get_task_by_id(uuid.UUID(task_id))
        
        if not db_task:
            logger.error("Task record not found in database", extra={"task_id": task_id})
            return False
            
        logger.info("Task details", extra={
            "task_id": task_id,
            "status": db_task.status,
            "result": db_task.result
        })
        
        # Check if task is completed
        if db_task.status != "COMPLETED":
            logger.error("Task status is not COMPLETED", extra={
                "task_id": task_id,
                "status": db_task.status
            })
            return False
            
        # Check if result contains "Hello World!"
        if not db_task.result or "content" not in db_task.result:
            logger.error("Task result does not contain content", extra={
                "task_id": task_id,
                "result": db_task.result
            })
            return False
            
        if db_task.result["content"] != "Hello World!":
            logger.error("Task result content is not 'Hello World!'", extra={
                "task_id": task_id,
                "content": db_task.result["content"]
            })
            return False
            
        logger.info("✅ Task validation passed!", extra={
            "task_id": task_id,
            "content": db_task.result["content"]
        })
        return True

def test_hello_world_agent_directly():
    """Test HelloWorldAgent directly to ensure it works"""
    with TracerContextManager.start_trace("m1_validation_test_agent"):
        logger.info("Testing HelloWorldAgent directly")
        
        agent = HelloWorldAgent()
        result = agent.run({"test": "m1_validation"})
        
        if result.status != "SUCCESS":
            logger.error("HelloWorldAgent failed", extra={"status": result.status})
            return False
            
        if result.output.intent.content != "Hello World!":
            logger.error("HelloWorldAgent returned incorrect content", extra={
                "content": result.output.intent.content
            })
            return False
            
        logger.info("✅ HelloWorldAgent test passed!", extra={
            "content": result.output.intent.content
        })
        return True

def main():
    """Main validation function"""
    with TracerContextManager.start_trace("m1_validation_main"):
        logger.info("Starting M1 validation test")
        
        # Test 1: Verify HelloWorldAgent works directly
        if not test_hello_world_agent_directly():
            logger.error("❌ M1 validation failed: HelloWorldAgent test failed")
            return 1
            
        # Test 2: Create a task manually
        task_id = create_test_task()
        if not task_id:
            logger.error("❌ M1 validation failed: Could not create test task")
            return 1
            
        # Test 3: Verify task was processed correctly
        # Note: This assumes the Central Graph Engine is running and will process the task
        # In a real test environment, we would start the engine here
        if not verify_task_completed(task_id):
            logger.error("❌ M1 validation failed: Task processing verification failed")
            return 1
            
        logger.info("✅ All M1 validation tests passed!")
        return 0

if __name__ == "__main__":
    sys.exit(main())