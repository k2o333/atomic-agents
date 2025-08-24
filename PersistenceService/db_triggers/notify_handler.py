"""
Notify Handler Process for Persistence Service

This module implements a background process that listens for PostgreSQL NOTIFY events
and processes them accordingly, such as adding tasks to Redis queues for the 
Central Graph Engine to consume.
"""

import psycopg2
import redis
import json
import time
import logging
from typing import Optional
from ..config import DatabaseConfig

# Initialize logger
logger = logging.getLogger(__name__)

class NotifyHandler:
    """Handler for PostgreSQL NOTIFY events."""
    
    def __init__(self, db_config: Optional[DatabaseConfig] = None, 
                 redis_host: str = 'localhost', redis_port: int = 6379,
                 task_queue: str = 'task_execution_queue'):
        self.db_config = db_config or DatabaseConfig()
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.task_queue = task_queue
        self.db_connection = None
        self.redis_client = None
        
    def connect_to_database(self) -> None:
        """Establish connection to PostgreSQL database."""
        try:
            self.db_connection = psycopg2.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                database=self.db_config.database,
                user=self.db_config.user,
                password=self.db_config.password
            )
            self.db_connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            logger.info("Connected to PostgreSQL database for NOTIFY handling")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
            raise
    
    def connect_to_redis(self) -> None:
        """Establish connection to Redis server."""
        try:
            self.redis_client = redis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info("Connected to Redis server for NOTIFY handling")
        except Exception as e:
            logger.error(f"Failed to connect to Redis server: {str(e)}")
            raise
    
    def listen_for_notifications(self) -> None:
        """Listen for PostgreSQL NOTIFY events and process them."""
        if not self.db_connection:
            self.connect_to_database()
        
        if not self.redis_client:
            self.connect_to_redis()
        
        with self.db_connection.cursor() as cursor:
            # Listen for both task_updated and task_created events
            cursor.execute("LISTEN task_updated;")
            cursor.execute("LISTEN task_created;")
            logger.info("Started listening for PostgreSQL NOTIFY events")
            
            while True:
                # Check for notifications
                self.db_connection.poll()
                
                # Process any pending notifications
                while self.db_connection.notifies:
                    notify = self.db_connection.notifies.pop(0)
                    logger.info(f"Received NOTIFY: {notify.channel} - {notify.payload}")
                    
                    try:
                        # Parse the payload
                        payload = json.loads(notify.payload)
                        task_id = payload.get('task_id')
                        
                        if task_id:
                            # Add task to Redis queue for processing
                            self.redis_client.lpush(self.task_queue, task_id)
                            logger.info(f"Added task {task_id} to Redis queue '{self.task_queue}'")
                        else:
                            logger.warning(f"Received NOTIFY with no task_id: {payload}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse NOTIFY payload: {str(e)}")
                    except Exception as e:
                        logger.error(f"Error processing NOTIFY: {str(e)}")
                
                # Sleep briefly to avoid excessive CPU usage
                time.sleep(0.1)
    
    def start(self) -> None:
        """Start the notify handler process."""
        logger.info("Starting Notify Handler process")
        try:
            self.listen_for_notifications()
        except KeyboardInterrupt:
            logger.info("Received interrupt signal. Stopping Notify Handler...")
        except Exception as e:
            logger.error(f"Error in Notify Handler: {str(e)}")
        finally:
            if self.db_connection:
                self.db_connection.close()
                logger.info("Closed database connection")
    
    def stop(self) -> None:
        """Stop the notify handler process."""
        logger.info("Stopping Notify Handler process")
        if self.db_connection:
            self.db_connection.close()