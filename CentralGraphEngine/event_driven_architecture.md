# Central Graph Engine Enhanced Event-Driven Architecture

## Overview

This document describes the enhanced event-driven architecture for the Central Graph Engine, 
which replaces the polling-based approach with Redis BRPOP for task consumption and 
PostgreSQL triggers with NOTIFY handlers for real-time task queuing.

## Architecture Components

### 1. PostgreSQL Triggers and NOTIFY Handler (Infrastructure)

Located in: `PersistenceService/db_triggers/`

- **PostgreSQL Triggers**: Automatically send NOTIFY events when tasks are created or updated
- **Notify Handler**: Listens for NOTIFY events and adds tasks to Redis queues

### 2. Redis BRPOP Loop (Central Graph Engine)

Located in: `CentralGraphEngine/engine_enhanced.py`

- **BRPOP Loop**: Replaces polling with blocking Redis queue consumption
- **Event-Driven Processing**: Tasks are processed as soon as they are added to the queue

## How It Works

1. **Task Creation/Update**: When a task is created or updated in PostgreSQL, triggers automatically send NOTIFY events
2. **Notify Handler**: The NOTIFY handler process listens for these events and adds task IDs to Redis queues
3. **BRPOP Consumption**: The Central Graph Engine uses Redis BRPOP to blockingly wait for tasks in the queue
4. **Task Processing**: When a task is received, it's processed according to its type and status

## Benefits

- **Real-time Processing**: Tasks are processed immediately when they become available
- **Reduced Latency**: Eliminates polling delays
- **Lower Resource Usage**: No constant database polling
- **Scalability**: Multiple engine instances can consume from the same queue without conflict

## Deployment

1. Start the Notify Handler process:
   ```bash
   python PersistenceService/db_triggers/start_notify_handler.py
   ```

2. Start the Central Graph Engine:
   ```bash
   python CentralGraphEngine/engine_enhanced.py
   ```

## Configuration

Both components read configuration from environment variables:

- Database: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Redis: `--redis-host`, `--redis-port` command line arguments