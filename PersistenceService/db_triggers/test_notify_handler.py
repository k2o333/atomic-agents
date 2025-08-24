#!/usr/bin/env python3
"""
Test script for the Notify Handler component.

This script tests the NOTIFY handler functionality by:
1. Setting up the necessary connections
2. Simulating task creation/update in the database
3. Verifying that NOTIFY events are processed
4. Checking that tasks are added to Redis queues
"""

import sys
import os
import time
import json
import psycopg2
import redis
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PersistenceService.config import DatabaseConfig
from PersistenceService.db_triggers.notify_handler import NotifyHandler

def setup_test_database():
    """Set up test database with triggers."""
    db_config = DatabaseConfig()
    
    # Connect to database
    conn = psycopg2.connect(
        host=db_config.host,
        port=db_config.port,
        database=db_config.database,
        user=db_config.user,
        password=db_config.password
    )
    
    # Create tasks table if it doesn't exist
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                workflow_id UUID NOT NULL,
                assignee_id VARCHAR(255) NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
                input_data JSONB,
                result JSONB,
                directives JSONB,
                parent_task_id UUID,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        
        # Create the triggers
        cur.execute("""
            CREATE OR REPLACE FUNCTION notify_task_update()
            RETURNS TRIGGER AS $$
            DECLARE
                payload JSON;
            BEGIN
                payload = json_build_object(
                    'task_id', NEW.id,
                    'status', NEW.status,
                    'updated_at', NEW.updated_at
                );
                PERFORM pg_notify('task_updated', payload::text);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cur.execute("""
            DROP TRIGGER IF EXISTS task_update_trigger ON tasks;
            CREATE TRIGGER task_update_trigger
            AFTER UPDATE ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION notify_task_update();
        """)
        
        cur.execute("""
            CREATE OR REPLACE FUNCTION notify_task_creation()
            RETURNS TRIGGER AS $$
            DECLARE
                payload JSON;
            BEGIN
                payload = json_build_object(
                    'task_id', NEW.id,
                    'workflow_id', NEW.workflow_id,
                    'assignee_id', NEW.assignee_id,
                    'status', NEW.status,
                    'created_at', NEW.created_at
                );
                PERFORM pg_notify('task_created', payload::text);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cur.execute("""
            DROP TRIGGER IF EXISTS task_creation_trigger ON tasks;
            CREATE TRIGGER task_creation_trigger
            AFTER INSERT ON tasks
            FOR EACH ROW
            EXECUTE FUNCTION notify_task_creation();
        """)
        
        conn.commit()
    
    return conn

def test_notify_handler():
    """Test the notify handler functionality."""
    print("Setting up test environment...")
    
    # Set up database with triggers
    db_conn = setup_test_database()
    
    # Set up Redis connection
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Clear test queue
    test_queue = 'test_task_queue'
    redis_client.delete(test_queue)
    
    # Create notify handler
    notify_handler = NotifyHandler(
        redis_host='localhost',
        redis_port=6379,
        task_queue=test_queue
    )
    
    # Connect to database for notify handler
    notify_handler.connect_to_database()
    notify_handler.connect_to_redis()
    
    print("Test environment ready.")
    print("Testing task creation trigger...")
    
    # Create a test task
    task_id = str(uuid.uuid4())
    workflow_id = str(uuid.uuid4())
    
    with db_conn.cursor() as cur:
        cur.execute("""
            INSERT INTO tasks (id, workflow_id, assignee_id, status)
            VALUES (%s, %s, %s, %s)
        """, (task_id, workflow_id, 'Agent:TestWorker', 'PENDING'))
        db_conn.commit()
    
    print(f"Created task {task_id}")
    
    # Wait a moment for the NOTIFY to be processed
    time.sleep(1)
    
    # Check if task was added to Redis queue
    queue_length = redis_client.llen(test_queue)
    print(f"Redis queue length: {queue_length}")
    
    if queue_length > 0:
        task_from_queue = redis_client.lpop(test_queue)
        print(f"Task from queue: {task_from_queue}")
        if task_from_queue == task_id:
            print("✓ Task creation trigger test PASSED")
        else:
            print("✗ Task creation trigger test FAILED - wrong task ID")
    else:
        print("✗ Task creation trigger test FAILED - no task in queue")
    
    print("Testing task update trigger...")
    
    # Update the test task
    with db_conn.cursor() as cur:
        cur.execute("""
            UPDATE tasks SET status = %s, updated_at = NOW()
            WHERE id = %s
        """, ('COMPLETED', task_id))
        db_conn.commit()
    
    print(f"Updated task {task_id} to COMPLETED")
    
    # Wait a moment for the NOTIFY to be processed
    time.sleep(1)
    
    # Check if task was added to Redis queue again
    queue_length = redis_client.llen(test_queue)
    print(f"Redis queue length: {queue_length}")
    
    if queue_length > 0:
        task_from_queue = redis_client.lpop(test_queue)
        print(f"Task from queue: {task_from_queue}")
        if task_from_queue == task_id:
            print("✓ Task update trigger test PASSED")
        else:
            print("✗ Task update trigger test FAILED - wrong task ID")
    else:
        print("✗ Task update trigger test FAILED - no task in queue")
    
    # Clean up
    db_conn.close()
    
    print("Test completed.")

if __name__ == "__main__":
    test_notify_handler()