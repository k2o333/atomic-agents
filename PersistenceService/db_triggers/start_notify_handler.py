#!/usr/bin/env python3
"""
Main entry point for the Notify Handler process.

This script starts the PostgreSQL NOTIFY listener that adds tasks to Redis queues
when they are updated or created in the database.
"""

import sys
import os
import argparse
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from PersistenceService.db_triggers.notify_handler import NotifyHandler
from PersistenceService.config import DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    parser = argparse.ArgumentParser(description='Notify Handler for Persistence Service')
    parser.add_argument('--redis-host', default='localhost', help='Redis server hostname')
    parser.add_argument('--redis-port', type=int, default=6379, help='Redis server port')
    parser.add_argument('--task-queue', default='task_execution_queue', help='Redis queue name for tasks')
    
    args = parser.parse_args()
    
    # Create and start the notify handler
    notify_handler = NotifyHandler(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        task_queue=args.task_queue
    )
    
    try:
        notify_handler.start()
    except KeyboardInterrupt:
        print("\nShutting down Notify Handler...")
        notify_handler.stop()
    except Exception as e:
        print(f"Error in Notify Handler: {str(e)}")
        notify_handler.stop()
        sys.exit(1)

if __name__ == "__main__":
    main()