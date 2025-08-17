"""
Unit tests for TaskHistoryRepository
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from uuid import UUID
from datetime import datetime

from PersistenceService.repository.task_history_repository import TaskHistoryRepository
from PersistenceService.models.task import TaskHistoryRecord

class TestTaskHistoryRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_manager = Mock()
        self.history_repo = TaskHistoryRepository(self.mock_db_manager)
    
    @patch('PersistenceService.repository.task_history_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_history_repository.logger')
    def test_create_task_history_record(self, mock_logger, mock_tracer):
        """Test creating a new task history record."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = [UUID('123e4567-e89b-12d3-a456-426614174000')]
        
        # Mock the context managers properly
        mock_db_session_context = Mock()
        mock_db_session_context.__enter__ = Mock(return_value=mock_conn)
        mock_db_session_context.__exit__ = Mock(return_value=None)
        self.mock_db_manager.get_db_session = Mock(return_value=mock_db_session_context)
        
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_conn.cursor = Mock(return_value=mock_cursor_context)
        
        # Call the method
        history_id = self.history_repo.create_task_history_record(
            task_id=UUID('123e4567-e89b-12d3-a456-426614174001'),
            version_number=1,
            data_snapshot={"test": "data"}
        )
        
        # Assertions
        self.assertEqual(history_id, UUID('123e4567-e89b-12d3-a456-426614174000'))
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.task_history_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_history_repository.logger')
    def test_get_task_history_by_id_found(self, mock_logger, mock_tracer):
        """Test getting a task history record by ID when it exists."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            UUID('123e4567-e89b-12d3-a456-426614174000'),
            UUID('123e4567-e89b-12d3-a456-426614174001'),
            1,
            {"test": "data"},
            datetime.now()
        )
        
        # Mock the context managers properly
        mock_db_session_context = Mock()
        mock_db_session_context.__enter__ = Mock(return_value=mock_conn)
        mock_db_session_context.__exit__ = Mock(return_value=None)
        self.mock_db_manager.get_db_session = Mock(return_value=mock_db_session_context)
        
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_conn.cursor = Mock(return_value=mock_cursor_context)
        
        # Call the method
        history_record = self.history_repo.get_task_history_by_id(UUID('123e4567-e89b-12d3-a456-426614174000'))
        
        # Assertions
        self.assertIsNotNone(history_record)
        self.assertIsInstance(history_record, TaskHistoryRecord)
        self.assertEqual(history_record.id, UUID('123e4567-e89b-12d3-a456-426614174000'))
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.task_history_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_history_repository.logger')
    def test_get_task_history_by_id_not_found(self, mock_logger, mock_tracer):
        """Test getting a task history record by ID when it doesn't exist."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        # Mock the context managers properly
        mock_db_session_context = Mock()
        mock_db_session_context.__enter__ = Mock(return_value=mock_conn)
        mock_db_session_context.__exit__ = Mock(return_value=None)
        self.mock_db_manager.get_db_session = Mock(return_value=mock_db_session_context)
        
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_conn.cursor = Mock(return_value=mock_cursor_context)
        
        # Call the method
        history_record = self.history_repo.get_task_history_by_id(UUID('123e4567-e89b-12d3-a456-426614174000'))
        
        # Assertions
        self.assertIsNone(history_record)
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.task_history_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_history_repository.logger')
    def test_get_task_history_by_task_id(self, mock_logger, mock_tracer):
        """Test getting task history records by task ID."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (
                UUID('123e4567-e89b-12d3-a456-426614174000'),
                UUID('123e4567-e89b-12d3-a456-426614174001'),
                1,
                {"test": "data"},
                datetime.now()
            ),
            (
                UUID('123e4567-e89b-12d3-a456-426614174002'),
                UUID('123e4567-e89b-12d3-a456-426614174001'),
                2,
                {"test": "data2"},
                datetime.now()
            )
        ]
        
        # Mock the context managers properly
        mock_db_session_context = Mock()
        mock_db_session_context.__enter__ = Mock(return_value=mock_conn)
        mock_db_session_context.__exit__ = Mock(return_value=None)
        self.mock_db_manager.get_db_session = Mock(return_value=mock_db_session_context)
        
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_conn.cursor = Mock(return_value=mock_cursor_context)
        
        # Call the method
        history_records = self.history_repo.get_task_history_by_task_id(UUID('123e4567-e89b-12d3-a456-426614174001'))
        
        # Assertions
        self.assertEqual(len(history_records), 2)
        self.assertIsInstance(history_records[0], TaskHistoryRecord)
        self.assertEqual(history_records[0].task_id, UUID('123e4567-e89b-12d3-a456-426614174001'))
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.task_history_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_history_repository.logger')
    def test_get_latest_task_history_found(self, mock_logger, mock_tracer):
        """Test getting the latest task history record when it exists."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (
            UUID('123e4567-e89b-12d3-a456-426614174000'),
            UUID('123e4567-e89b-12d3-a456-426614174001'),
            2,
            {"test": "data"},
            datetime.now()
        )
        
        # Mock the context managers properly
        mock_db_session_context = Mock()
        mock_db_session_context.__enter__ = Mock(return_value=mock_conn)
        mock_db_session_context.__exit__ = Mock(return_value=None)
        self.mock_db_manager.get_db_session = Mock(return_value=mock_db_session_context)
        
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_conn.cursor = Mock(return_value=mock_cursor_context)
        
        # Call the method
        history_record = self.history_repo.get_latest_task_history(UUID('123e4567-e89b-12d3-a456-426614174001'))
        
        # Assertions
        self.assertIsNotNone(history_record)
        self.assertIsInstance(history_record, TaskHistoryRecord)
        self.assertEqual(history_record.version_number, 2)
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.task_history_repository.TracerContextManager')
    @patch('PersistenceService.repository.task_history_repository.logger')
    def test_get_latest_task_history_not_found(self, mock_logger, mock_tracer):
        """Test getting the latest task history record when none exists."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = None
        
        # Mock the context managers properly
        mock_db_session_context = Mock()
        mock_db_session_context.__enter__ = Mock(return_value=mock_conn)
        mock_db_session_context.__exit__ = Mock(return_value=None)
        self.mock_db_manager.get_db_session = Mock(return_value=mock_db_session_context)
        
        mock_cursor_context = Mock()
        mock_cursor_context.__enter__ = Mock(return_value=mock_cursor)
        mock_cursor_context.__exit__ = Mock(return_value=None)
        mock_conn.cursor = Mock(return_value=mock_cursor_context)
        
        # Call the method
        history_record = self.history_repo.get_latest_task_history(UUID('123e4567-e89b-12d3-a456-426614174001'))
        
        # Assertions
        self.assertIsNone(history_record)
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()

if __name__ == '__main__':
    unittest.main()