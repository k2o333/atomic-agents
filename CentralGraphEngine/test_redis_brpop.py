#!/usr/bin/env python3
"""
Test script for the Central Graph Engine Redis BRPOP loop.

This script tests the Redis BRPOP functionality by:
1. Adding tasks to a Redis queue
2. Verifying that the Central Graph Engine can consume them
"""

import sys
import os
import time
import redis
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def test_redis_brpop():
    """Test the Redis BRPOP functionality."""
    print("Setting up test environment...")
    
    # Set up Redis connection
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Clear test queue
    test_queue = 'test_task_queue'
    redis_client.delete(test_queue)
    
    print("Adding tasks to Redis queue...")
    
    # Add some test tasks to the queue
    task_ids = []
    for i in range(3):
        task_id = str(uuid.uuid4())
        task_ids.append(task_id)
        redis_client.lpush(test_queue, task_id)
        print(f"Added task {task_id} to queue")
    
    print("Tasks added to queue. Testing BRPOP functionality...")
    print("Run the Central Graph Engine to consume these tasks.")
    
    # Wait a bit and check if tasks were consumed
    time.sleep(5)
    
    queue_length = redis_client.llen(test_queue)
    print(f"Redis queue length after waiting: {queue_length}")
    
    if queue_length == 0:
        print("✓ All tasks were consumed from the queue")
    else:
        print(f"✗ {queue_length} tasks remain in the queue")
        # Clean up remaining tasks
        while redis_client.llen(test_queue) > 0:
            task = redis_client.lpop(test_queue)
            print(f"Remaining task in queue: {task}")

if __name__ == "__main__":
    test_redis_brpop()