"""
Unit tests for TaskRepository
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from uuid import UUID
from datetime import datetime

from PersistenceService.repository.task_repository import TaskRepository
from PersistenceService.models.task import TaskRecord

class TestTaskRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_manager = Mock()
        self.task_repo = TaskRepository(self.mock_db_manager)
    
    @patch('PersistenceService.repository.task_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_repository.logger')
    def test_create_task(self, mock_logger, mock_tracer):
        """Test creating a new task."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_session = Mock()
        mock_db_session.__enter__.return_value = mock_conn
        self.mock_db_manager.get_db_session.return_value = mock_db_session
        
        # Mock the cursor execute and fetchone
        mock_cursor.fetchone.return_value = [UUID('123e4567-e89b-12d3-a456-426614174000')]
        
        # Call the method
        task_id = self.task_repo.create_task(
            workflow_id=UUID('123e4567-e89b-12d3-a456-426614174001'),
            assignee_id="Agent:Worker",
            input_data={"test": "data"}
        )
        
        # Assertions
        self.assertEqual(task_id, UUID('123e4567-e89b-12d3-a456-426614174000'))
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.task_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_repository.logger')
    def test_get_task_by_id_found(self, mock_logger, mock_tracer):
        """Test getting a task by ID when it exists."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_session = Mock()
        mock_db_session.__enter__.return_value = mock_conn
        self.mock_db_manager.get_db_session.return_value = mock_db_session
        
        # Mock the cursor execute and fetchone
        mock_cursor.fetchone.return_value = (
            UUID('123e4567-e89b-12d3-a456-426614174000'),
            UUID('123e4567-e89b-12d3-a456-426614174001'),
            "Agent:Worker",
            "PENDING",
            {"test": "data"},
            None,
            None,
            None,
            datetime.now(),
            datetime.now()
        )
        
        # Call the method
        task = self.task_repo.get_task_by_id(UUID('123e4567-e89b-12d3-a456-426614174000'))
        
        # Assertions
        self.assertIsNotNone(task)
        self.assertIsInstance(task, TaskRecord)
        self.assertEqual(task.id, UUID('123e4567-e89b-12d3-a456-426614174000'))
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.task_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_repository.logger')
    def test_get_task_by_id_not_found(self, mock_logger, mock_tracer):
        """Test getting a task by ID when it doesn't exist."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_session = Mock()
        mock_db_session.__enter__.return_value = mock_conn
        self.mock_db_manager.get_db_session.return_value = mock_db_session
        
        # Mock the cursor execute and fetchone
        mock_cursor.fetchone.return_value = None
        
        # Call the method
        task = self.task_repo.get_task_by_id(UUID('123e4567-e89b-12d3-a456-426614174000'))
        
        # Assertions
        self.assertIsNone(task)
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.task_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_repository.logger')
    def test_update_task_status(self, mock_logger, mock_tracer):
        """Test updating task status."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_session = Mock()
        mock_db_session.__enter__.return_value = mock_conn
        self.mock_db_manager.get_db_session.return_value = mock_db_session
        
        # Mock the cursor rowcount
        mock_cursor.rowcount = 1
        
        # Call the method
        updated = self.task_repo.update_task_status(
            task_id=UUID('123e4567-e89b-12d3-a456-426614174000'),
            status="COMPLETED",
            result={"output": "test result"}
        )
        
        # Assertions
        self.assertTrue(updated)
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()

if __name__ == '__main__':
    unittest.main()