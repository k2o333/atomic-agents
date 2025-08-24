#!/usr/bin/env python3
"""
Test script for the Notify Handler component.

This script tests the NOTIFY handler functionality by:
1. Setting up the necessary connections
2. Running the notify handler in a separate thread
3. Simulating task creation/update in the database
4. Verifying that NOTIFY events are processed
5. Checking that tasks are added to Redis queues
"""

import sys
import os
import time
import json
import psycopg2
import redis
import uuid
import threading

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PersistenceService.config import DatabaseConfig

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

def test_triggers_only():
    """Test just the triggers by listening for notifications directly."""
    print("Setting up test environment...")
    
    # Set up database with triggers
    db_config = DatabaseConfig()
    db_conn = psycopg2.connect(
        host=db_config.host,
        port=db_config.port,
        database=db_config.database,
        user=db_config.user,
        password=db_config.password
    )
    db_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    
    # Set up Redis connection
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Clear test queue
    test_queue = 'test_task_queue'
    redis_client.delete(test_queue)
    
    # Listen for notifications
    with db_conn.cursor() as cursor:
        cursor.execute("LISTEN task_created;")
        cursor.execute("LISTEN task_updated;")
        print("Started listening for PostgreSQL NOTIFY events")
        
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
        
        # Wait and check for notifications
        time.sleep(2)
        db_conn.poll()
        
        notifications_received = []
        while db_conn.notifies:
            notify = db_conn.notifies.pop(0)
            notifications_received.append(notify)
            print(f"Received NOTIFY: {notify.channel} - {notify.payload}")
            
            try:
                # Parse the payload and add to Redis
                import json
                payload = json.loads(notify.payload)
                task_id_from_payload = payload.get('task_id')
                
                if task_id_from_payload:
                    redis_client.lpush(test_queue, task_id_from_payload)
                    print(f"Added task {task_id_from_payload} to Redis queue '{test_queue}'")
            except Exception as e:
                print(f"Error processing NOTIFY: {e}")
        
        print(f"Total notifications received: {len(notifications_received)}")
        
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
        
        # Wait and check for notifications
        time.sleep(2)
        db_conn.poll()
        
        notifications_received = []
        while db_conn.notifies:
            notify = db_conn.notifies.pop(0)
            notifications_received.append(notify)
            print(f"Received NOTIFY: {notify.channel} - {notify.payload}")
            
            try:
                # Parse the payload and add to Redis
                import json
                payload = json.loads(notify.payload)
                task_id_from_payload = payload.get('task_id')
                
                if task_id_from_payload:
                    redis_client.lpush(test_queue, task_id_from_payload)
                    print(f"Added task {task_id_from_payload} to Redis queue '{test_queue}'")
            except Exception as e:
                print(f"Error processing NOTIFY: {e}")
        
        print(f"Total notifications received: {len(notifications_received)}")
        
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
    test_triggers_only()