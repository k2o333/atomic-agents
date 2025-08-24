# Database Triggers and Notify Handler

## Overview

This directory contains the PostgreSQL triggers and notify handler implementation for the Persistence Service. These components enable event-driven architecture by automatically sending notifications when tasks are created or updated in the database.

## Components

### PostgreSQL Triggers (`task_triggers.sql`)

The SQL script defines two triggers:

1. `task_update_trigger` - Fires when a task is updated
2. `task_creation_trigger` - Fires when a new task is created

Both triggers call functions that send `NOTIFY` events with JSON payloads containing task information.

### Notify Handler (`notify_handler.py`)

A Python process that listens for PostgreSQL `NOTIFY` events and adds tasks to Redis queues for the Central Graph Engine to consume.

### Entry Point (`start_notify_handler.py`)

A script to start the notify handler process with configurable Redis connection parameters.

## How It Works

1. When a task is created or updated in the database, the PostgreSQL triggers automatically send `NOTIFY` events
2. The Notify Handler process listens for these events
3. When an event is received, the handler adds the task ID to a Redis queue
4. The Central Graph Engine consumes tasks from this Redis queue using `BRPOP`

## Deployment

To start the notify handler:

```bash
python start_notify_handler.py --redis-host localhost --redis-port 6379 --task-queue task_execution_queue
```

## Configuration

The notify handler uses the same database configuration as the Persistence Service, reading from environment variables:

- `DB_HOST` - PostgreSQL host (default: localhost)
- `DB_PORT` - PostgreSQL port (default: 5432)
- `DB_NAME` - Database name (default: synapse)
- `DB_USER` - Database user (default: synapse_user)
- `DB_PASSWORD` - Database password (default: synapse_password)