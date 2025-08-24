"""
PostgreSQL Triggers for Persistence Service

This module defines PostgreSQL triggers that automatically send NOTIFY events
when tasks are updated, enabling real-time event-driven processing.
"""

-- Function to send notification when a task is updated
CREATE OR REPLACE FUNCTION notify_task_update()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    -- Create a JSON payload with task information
    payload = json_build_object(
        'task_id', NEW.id,
        'status', NEW.status,
        'updated_at', NEW.updated_at
    );
    
    -- Send notification with the task ID as the payload
    PERFORM pg_notify('task_updated', payload::text);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the notification function after task updates
DROP TRIGGER IF EXISTS task_update_trigger ON tasks;
CREATE TRIGGER task_update_trigger
AFTER UPDATE ON tasks
FOR EACH ROW
EXECUTE FUNCTION notify_task_update();

-- Function to send notification when a new task is created
CREATE OR REPLACE FUNCTION notify_task_creation()
RETURNS TRIGGER AS $$
DECLARE
    payload JSON;
BEGIN
    -- Create a JSON payload with task information
    payload = json_build_object(
        'task_id', NEW.id,
        'workflow_id', NEW.workflow_id,
        'assignee_id', NEW.assignee_id,
        'status', NEW.status,
        'created_at', NEW.created_at
    );
    
    -- Send notification with the task ID as the payload
    PERFORM pg_notify('task_created', payload::text);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to call the notification function after task creation
DROP TRIGGER IF EXISTS task_creation_trigger ON tasks;
CREATE TRIGGER task_creation_trigger
AFTER INSERT ON tasks
FOR EACH ROW
EXECUTE FUNCTION notify_task_creation();