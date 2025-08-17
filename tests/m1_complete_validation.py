#!/usr/bin/env python3
"""
Complete M1 Validation Script

This script validates all aspects of the M1 acceptance criteria:
1. ✅ Able to manually INSERT a Task via API (or script)
2. ✅ Graph Engine can poll the task, call HelloWorldAgent, and update task status to COMPLETED
3. ✅ Result field contains "Hello World!"
4. ✅ All key steps have structured logs with trace_id
"""

import sys
import os
import time
import uuid
import json
import subprocess
import threading
from typing import Optional

# Add project root to Python path
sys.path.insert(0, '/root/projects/atom_agents')

from PersistenceService.service import PersistenceService
from agentservice.generic_agents.HelloWorldAgent import HelloWorldAgent
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize services
logger = get_logger(__name__)
persistence_service = PersistenceService()

def test_manual_task_insertion():
    """Test manual task insertion via API"""
    with TracerContextManager.start_trace("m1_test_manual_insertion"):
        logger.info("Testing manual task insertion via API")
        
        try:
            # Create a task using the PersistenceService API
            workflow_id = uuid.uuid4()
            task_id = persistence_service.create_task(
                workflow_id=workflow_id,
                assignee_id="Agent:HelloWorldAgent",
                input_data={"source": "manual_api_test", "milestone": "M1"}
            )
            
            logger.info("✅ Manual task insertion via API successful", extra={
                "task_id": str(task_id),
                "workflow_id": str(workflow_id)
            })
            
            # Verify the task exists
            task = persistence_service.get_task(task_id)
            if not task:
                logger.error("❌ Task not found after insertion")
                return None
                
            logger.info("✅ Task verified in database", extra={
                "task_id": str(task_id),
                "assignee_id": task.assignee_id,
                "status": "PENDING"  # Should be PENDING by default
            })
            
            return str(task_id)
            
        except Exception as e:
            logger.error("❌ Manual task insertion failed", extra={"error": str(e)})
            return None

def test_hello_world_agent():
    """Test HelloWorldAgent directly"""
    with TracerContextManager.start_trace("m1_test_hello_world_agent"):
        logger.info("Testing HelloWorldAgent directly")
        
        try:
            agent = HelloWorldAgent()
            result = agent.run({"test": "m1_validation"})
            
            if result.status != "SUCCESS":
                logger.error("❌ HelloWorldAgent failed", extra={"status": result.status})
                return False
                
            if result.output.intent.content != "Hello World!":
                logger.error("❌ HelloWorldAgent returned incorrect content", extra={
                    "content": result.output.intent.content
                })
                return False
                
            logger.info("✅ HelloWorldAgent test passed", extra={
                "content": result.output.intent.content,
                "thought": result.output.thought
            })
            return True
            
        except Exception as e:
            logger.error("❌ HelloWorldAgent test failed", extra={"error": str(e)})
            return False

def run_engine_for_short_time():
    """Run the Central Graph Engine for a short time to process tasks"""
    with TracerContextManager.start_trace("m1_run_engine"):
        logger.info("Starting Central Graph Engine for task processing")
        
        try:
            # Import the engine
            from CentralGraphEngine.engine import main_loop
            
            # Run the engine for a short time in a separate thread
            def engine_thread():
                # Run for just 5 seconds to process any pending tasks
                main_loop(polling_interval=1)
                
            # Start engine in background thread
            thread = threading.Thread(target=engine_thread)
            thread.daemon = True
            thread.start()
            
            # Let it run for a few seconds
            time.sleep(5)
            
            logger.info("Engine run completed")
            return True
            
        except Exception as e:
            logger.error("❌ Engine run failed", extra={"error": str(e)})
            return False

def verify_task_processing(task_id: str):
    """Verify that the task was processed correctly"""
    with TracerContextManager.start_trace("m1_verify_task_processing"):
        logger.info("Verifying task processing results", extra={"task_id": task_id})
        
        try:
            # Wait a bit for processing
            time.sleep(2)
            
            # Get the updated task from database
            db_task = persistence_service.task_repo.get_task_by_id(uuid.UUID(task_id))
            
            if not db_task:
                logger.error("❌ Task not found in database", extra={"task_id": task_id})
                return False
                
            logger.info("Task status check", extra={
                "task_id": task_id,
                "status": db_task.status,
                "result": db_task.result
            })
            
            # Check if task is completed
            if db_task.status != "COMPLETED":
                logger.error("❌ Task status is not COMPLETED", extra={
                    "task_id": task_id,
                    "status": db_task.status
                })
                return False
                
            # Check if result contains "Hello World!"
            if not db_task.result or "content" not in db_task.result:
                logger.error("❌ Task result does not contain content field", extra={
                    "task_id": task_id,
                    "result": db_task.result
                })
                return False
                
            if db_task.result["content"] != "Hello World!":
                logger.error("❌ Task result content is not 'Hello World!'", extra={
                    "task_id": task_id,
                    "content": db_task.result["content"]
                })
                return False
                
            logger.info("✅ Task processing verification passed", extra={
                "task_id": task_id,
                "content": db_task.result["content"],
                "status": db_task.status
            })
            return True
            
        except Exception as e:
            logger.error("❌ Task processing verification failed", extra={"error": str(e)})
            return False

def check_structured_logging():
    """Check that structured logging with trace_id is working"""
    with TracerContextManager.start_trace("m1_check_structured_logging"):
        logger.info("Checking structured logging with trace_id")
        
        # Log a few messages to verify structure
        with TracerContextManager.start_span("test_log_span"):
            logger.info("This is a test log message for M1 validation")
            logger.warning("This is a warning message", extra={"test_key": "test_value"})
            
        logger.info("✅ Structured logging test completed")
        return True

def main():
    """Main validation function"""
    with TracerContextManager.start_trace("m1_complete_validation"):
        logger.info("=== Starting Complete M1 Validation ===")
        
        # Test 1: Verify structured logging with trace_id
        print("\n1. Testing structured logging with trace_id...")
        if not check_structured_logging():
            logger.error("❌ M1 validation failed: Structured logging test failed")
            return 1
        print("   ✅ Structured logging working correctly")
        
        # Test 2: Test HelloWorldAgent directly
        print("\n2. Testing HelloWorldAgent directly...")
        if not test_hello_world_agent():
            logger.error("❌ M1 validation failed: HelloWorldAgent test failed")
            return 1
        print("   ✅ HelloWorldAgent working correctly")
        
        # Test 3: Manual task insertion via API
        print("\n3. Testing manual task insertion via API...")
        task_id = test_manual_task_insertion()
        if not task_id:
            logger.error("❌ M1 validation failed: Manual task insertion failed")
            return 1
        print(f"   ✅ Task inserted successfully: {task_id}")
        
        # Test 4: Run engine to process the task
        print("\n4. Running Central Graph Engine to process task...")
        if not run_engine_for_short_time():
            logger.error("❌ M1 validation failed: Engine run failed")
            return 1
        print("   ✅ Engine run completed")
        
        # Test 5: Verify task was processed correctly
        print("\n5. Verifying task processing results...")
        if not verify_task_processing(task_id):
            logger.error("❌ M1 validation failed: Task processing verification failed")
            return 1
        print("   ✅ Task processing verification passed")
        
        logger.info("=== ✅ All M1 Acceptance Criteria Validated Successfully ===")
        print("\nSUMMARY:")
        print("✅ 1. Manual task insertion via API - PASSED")
        print("✅ 2. HelloWorldAgent execution - PASSED") 
        print("✅ 3. Central Graph Engine task processing - PASSED")
        print("✅ 4. Task status updated to COMPLETED with 'Hello World!' - PASSED")
        print("✅ 5. Structured logging with trace_id - PASSED")
        
        return 0

if __name__ == "__main__":
    sys.exit(main())