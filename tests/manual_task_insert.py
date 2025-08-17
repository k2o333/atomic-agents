#!/usr/bin/env python3
"""
Manual Task Insert Script

This script demonstrates how to manually insert a Task into the database
to satisfy the M1 acceptance criteria.
"""

import sys
import os
import uuid
import json
import psycopg2
from typing import Optional

# Add project root to Python path
sys.path.insert(0, '/root/projects/atom_agents')

from PersistenceService.config import DatabaseConfig

def manual_insert_task():
    """Manually insert a task into the database using raw SQL"""
    print("Manually inserting a task into the database...")
    
    # Get database configuration
    config = DatabaseConfig()
    
    # Create a direct database connection
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        database=config.database,
        user=config.user,
        password=config.password
    )
    
    try:
        with conn.cursor() as cur:
            # Generate IDs
            task_id = uuid.uuid4()
            workflow_id = uuid.uuid4()
            
            # Insert task directly using SQL
            cur.execute("""
                INSERT INTO tasks (id, workflow_id, assignee_id, status, input_data)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                str(task_id),
                str(workflow_id),
                'Agent:HelloWorldAgent',
                'PENDING',
                json.dumps({"source": "manual_insert", "test": "m1_validation"})
            ))
            
            conn.commit()
            
            print(f"✅ Task inserted successfully!")
            print(f"   Task ID: {task_id}")
            print(f"   Workflow ID: {workflow_id}")
            print(f"   Assignee: Agent:HelloWorldAgent")
            print(f"   Status: PENDING")
            
            return str(task_id)
            
    except Exception as e:
        print(f"❌ Error inserting task: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def verify_task_inserted(task_id: str):
    """Verify the task was inserted correctly"""
    print(f"\nVerifying task {task_id} was inserted...")
    
    # Get database configuration
    config = DatabaseConfig()
    
    # Create a direct database connection
    conn = psycopg2.connect(
        host=config.host,
        port=config.port,
        database=config.database,
        user=config.user,
        password=config.password
    )
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, workflow_id, assignee_id, status, input_data, result
                FROM tasks
                WHERE id = %s
            """, (task_id,))
            
            row = cur.fetchone()
            if row:
                print(f"✅ Task found in database:")
                print(f"   ID: {row[0]}")
                print(f"   Workflow ID: {row[1]}")
                print(f"   Assignee: {row[2]}")
                print(f"   Status: {row[3]}")
                print(f"   Input Data: {row[4]}")
                print(f"   Result: {row[5]}")
                return True
            else:
                print(f"❌ Task not found in database")
                return False
                
    except Exception as e:
        print(f"❌ Error verifying task: {e}")
        return False
    finally:
        conn.close()

def main():
    """Main function to demonstrate manual task insertion"""
    print("=== M1 Manual Task Insertion Demo ===")
    
    try:
        # Insert a task manually
        task_id = manual_insert_task()
        
        # Verify it was inserted
        if verify_task_inserted(task_id):
            print(f"\n✅ Manual task insertion validation passed!")
            print(f"Task {task_id} can now be processed by the Central Graph Engine.")
            return 0
        else:
            print(f"\n❌ Manual task insertion validation failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Manual task insertion failed with error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())