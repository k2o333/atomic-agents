-- SQL script to initialize the database tables and triggers for Synapse Platform

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create tasks table (MVP enhanced version)
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
);

-- Create edges table (MVP enhanced version)
CREATE TABLE IF NOT EXISTS edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL,
    source_task_id UUID NOT NULL,
    target_task_id UUID NOT NULL,
    condition JSONB,
    data_flow JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_tasks_workflow_id ON tasks (workflow_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_id ON tasks (assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_parent_task_id ON tasks (parent_task_id);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks (created_at);

CREATE INDEX IF NOT EXISTS idx_edges_workflow_id ON edges (workflow_id);
CREATE INDEX IF NOT EXISTS idx_edges_source_task_id ON edges (source_task_id);
CREATE INDEX IF NOT EXISTS idx_edges_target_task_id ON edges (target_task_id);
CREATE INDEX IF NOT EXISTS idx_edges_created_at ON edges (created_at);

-- Create GIN indexes for JSONB fields to enable efficient querying
CREATE INDEX IF NOT EXISTS idx_tasks_input_data ON tasks USING GIN (input_data);
CREATE INDEX IF NOT EXISTS idx_tasks_result ON tasks USING GIN (result);
CREATE INDEX IF NOT EXISTS idx_edges_condition ON edges USING GIN (condition);
CREATE INDEX IF NOT EXISTS idx_edges_data_flow ON edges USING GIN (data_flow);

-- Create task_history table for versioning support (Milestone 3)
CREATE TABLE IF NOT EXISTS task_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL,
    version_number INTEGER NOT NULL,
    data_snapshot JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for task_history
CREATE INDEX IF NOT EXISTS idx_task_history_task_id ON task_history (task_id);
CREATE INDEX IF NOT EXISTS idx_task_history_version_number ON task_history (version_number);
CREATE INDEX IF NOT EXISTS idx_task_history_created_at ON task_history (created_at);

-- Create function to notify task updates
CREATE OR REPLACE FUNCTION notify_task_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Notify when task status changes to COMPLETED or FAILED
    IF (TG_OP = 'UPDATE' AND OLD.status IS DISTINCT FROM NEW.status AND 
        (NEW.status = 'COMPLETED' OR NEW.status = 'FAILED')) THEN
        PERFORM pg_notify('task_status_change', NEW.id::text);
    END IF;
    
    -- Notify when a new task is created
    IF (TG_OP = 'INSERT') THEN
        PERFORM pg_notify('task_created', NEW.id::text);
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for tasks table
DROP TRIGGER IF EXISTS task_status_change_trigger ON tasks;
CREATE TRIGGER task_status_change_trigger
    AFTER INSERT OR UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION notify_task_update();

-- Create function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at on tasks table
DROP TRIGGER IF EXISTS update_tasks_updated_at ON tasks;
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();