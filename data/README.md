# Database Configuration and Deployment

This directory contains the configuration files and initialization scripts for the PostgreSQL database used by the Synapse platform.

## Directory Structure

- `Dockerfile`: Dockerfile for building the PostgreSQL image with required extensions
- `postgresql.conf`: PostgreSQL configuration file optimized for the Synapse platform
- `sql/`: Directory containing SQL initialization scripts
  - `init_db_with_triggers.sql`: Database schema and triggers initialization script
- `postgres/`: Directory for PostgreSQL data persistence (mounted as a volume)

## Database Configuration

The database is configured with the following parameters:

- Host: 192.168.88.20
- Port: 5432
- Database: maindb
- User: admin
- Password: password

These settings are reflected in the following files:
- `PersistenceService/config.py`: Application configuration
- `.env`: Environment variables file
- `docker-compose.yml`: Docker deployment configuration

## Extensions Installed

The PostgreSQL image includes the following extensions:

1. **pgcrypto**: For UUID generation
2. **pgvector**: For vector similarity search
3. **Apache AGE**: For graph database functionality

## Key Features

1. **JSONB Support**: Tables are designed with JSONB columns for flexible data storage
2. **GIN Indexes**: Optimized indexes for JSONB queries
3. **Triggers**: Automatic notifications for task status changes
4. **Connection Pooling**: Configured for efficient connection management

## Deployment

To deploy the database service:

```bash
docker-compose up -d
```

## Testing Connection

To verify the database connection, run:

```bash
python test_db_connection.py
```

## Schema Overview

The database includes the following tables:

1. **tasks**: Core table for storing task information
2. **edges**: Table for storing workflow connections between tasks
3. **task_history**: Table for versioning support

Each table includes appropriate indexes for performance optimization.