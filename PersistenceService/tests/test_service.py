"""
Integration tests for PersistenceService
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from uuid import UUID

from PersistenceService.service import PersistenceService
from interfaces import PlanBlueprint, TaskDefinition, EdgeDefinition
from uuid import UUID

class TestPersistenceService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('PersistenceService.service.DatabaseManager') as mock_db_manager_class:
            # Mock the database manager instance
            mock_db_manager = Mock()
            mock_db_manager_class.return_value = mock_db_manager
            
            self.persistence_service = PersistenceService()
            # Mock the repositories
            self.persistence_service.task_repo = Mock()
            self.persistence_service.edge_repo = Mock()
            self.persistence_service.task_history_repo = Mock()
            self.persistence_service.tx_manager = Mock()
    
    @patch('PersistenceService.service.TracerContextManager')
    @patch('PersistenceService.service.logger')
    def test_create_task(self, mock_logger, mock_tracer):
        """Test creating a task through the service."""
        # Mock the task repository
        self.persistence_service.task_repo.create_task.return_value = UUID('123e4567-e89b-12d3-a456-426614174000')
        
        # Call the method
        task_id = self.persistence_service.create_task(
            workflow_id=UUID('123e4567-e89b-12d3-a456-426614174001'),
            assignee_id="Agent:Worker",
            input_data={"test": "data"}
        )
        
        # Assertions
        self.assertEqual(task_id, UUID('123e4567-e89b-12d3-a456-426614174000'))
        self.persistence_service.task_repo.create_task.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.service.TracerContextManager')
    @patch('PersistenceService.service.logger')
    def test_get_task_found(self, mock_logger, mock_tracer):
        """Test getting a task through the service when it exists."""
        # Mock the task repository
        mock_db_task = Mock()
        mock_db_task.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_db_task.workflow_id = UUID('123e4567-e89b-12d3-a456-426614174001')
        mock_db_task.assignee_id = "Agent:Worker"
        mock_db_task.status = "PENDING"
        mock_db_task.input_data = {"test": "data"}
        mock_db_task.result = None
        mock_db_task.directives = None
        mock_db_task.parent_task_id = None
        mock_db_task.created_at = "2023-01-01T00:00:00"
        mock_db_task.updated_at = "2023-01-01T00:00:00"
        
        self.persistence_service.task_repo.get_task_by_id.return_value = mock_db_task
        
        # Call the method
        task = self.persistence_service.get_task(UUID('123e4567-e89b-12d3-a456-426614174000'))
        
        # Assertions
        self.assertIsNotNone(task)
        self.assertIsInstance(task, TaskDefinition)
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.service.TracerContextManager')
    @patch('PersistenceService.service.logger')
    def test_create_workflow_from_blueprint_success(self, mock_logger, mock_tracer):
        """Test creating a workflow from blueprint successfully."""
        # Mock the transaction manager context manager
        mock_tx_context_manager = Mock()
        mock_tx_context = Mock()
        mock_tx_context.__enter__ = Mock(return_value=mock_tx_context)
        mock_tx_context.__exit__ = Mock(return_value=None)
        mock_tx_context_manager.__enter__ = Mock(return_value=mock_tx_context)
        mock_tx_context_manager.__exit__ = Mock(return_value=None)
        self.persistence_service.tx_manager.transaction = Mock(return_value=mock_tx_context_manager)
        
        # Mock the repository methods that will be called within the transaction
        self.persistence_service.task_repo.create_task = Mock(return_value=UUID('123e4567-e89b-12d3-a456-426614174010'))
        self.persistence_service.edge_repo.create_edge = Mock(return_value=UUID('123e4567-e89b-12d3-a456-426614174011'))
        
        # Create a test blueprint
        blueprint = PlanBlueprint(
            workflow_id=UUID('123e4567-e89b-12d3-a456-426614174001'),
            new_tasks=[
                TaskDefinition(
                    task_id="123e4567-e89b-12d3-a456-426614174101",
                    input_data={"goal": "Test task"},
                    assignee_id="Agent:Worker"
                )
            ],
            new_edges=[
                EdgeDefinition(
                    source_task_id="123e4567-e89b-12d3-a456-426614174101",
                    target_task_id="123e4567-e89b-12d3-a456-426614174102"
                )
            ]
        )
        
        # Call the method
        result = self.persistence_service.create_workflow_from_blueprint(blueprint)
        
        # Assertions
        self.assertTrue(result)
        self.persistence_service.tx_manager.transaction.assert_called_once()
        self.persistence_service.task_repo.create_task.assert_called_once()
        self.persistence_service.edge_repo.create_edge.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.service.TracerContextManager')
    @patch('PersistenceService.service.logger')
    def test_create_task_history_record(self, mock_logger, mock_tracer):
        """Test creating a task history record through the service."""
        # Mock the task history repository
        self.persistence_service.task_history_repo.create_task_history_record.return_value = UUID('123e4567-e89b-12d3-a456-426614174000')
        
        # Call the method
        history_id = self.persistence_service.create_task_history_record(
            task_id=UUID('123e4567-e89b-12d3-a456-426614174001'),
            version_number=1,
            data_snapshot={"test": "data"}
        )
        
        # Assertions
        self.assertEqual(history_id, UUID('123e4567-e89b-12d3-a456-426614174000'))
        self.persistence_service.task_history_repo.create_task_history_record.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.service.TracerContextManager')
    @patch('PersistenceService.service.logger')
    def test_get_task_history_by_task_id(self, mock_logger, mock_tracer):
        """Test getting task history records through the service."""
        # Mock the task history repository
        mock_history_record = Mock()
        mock_history_record.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_history_record.task_id = UUID('123e4567-e89b-12d3-a456-426614174001')
        mock_history_record.version_number = 1
        mock_history_record.data_snapshot = {"test": "data"}
        mock_history_record.created_at = "2023-01-01T00:00:00"
        
        self.persistence_service.task_history_repo.get_task_history_by_task_id.return_value = [mock_history_record]
        
        # Call the method
        history_records = self.persistence_service.get_task_history_by_task_id(UUID('123e4567-e89b-12d3-a456-426614174001'))
        
        # Assertions
        self.assertEqual(len(history_records), 1)
        self.assertIsInstance(history_records, list)
        self.assertEqual(history_records[0]["task_id"], str(UUID('123e4567-e89b-12d3-a456-426614174001')))
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.service.TracerContextManager')
    @patch('PersistenceService.service.logger')
    def test_get_latest_task_history_found(self, mock_logger, mock_tracer):
        """Test getting the latest task history record through the service when it exists."""
        # Mock the task history repository
        mock_history_record = Mock()
        mock_history_record.id = UUID('123e4567-e89b-12d3-a456-426614174000')
        mock_history_record.task_id = UUID('123e4567-e89b-12d3-a456-426614174001')
        mock_history_record.version_number = 2
        mock_history_record.data_snapshot = {"test": "data"}
        mock_history_record.created_at = "2023-01-01T00:00:00"
        
        self.persistence_service.task_history_repo.get_latest_task_history.return_value = mock_history_record
        
        # Call the method
        history_record = self.persistence_service.get_latest_task_history(UUID('123e4567-e89b-12d3-a456-426614174001'))
        
        # Assertions
        self.assertIsNotNone(history_record)
        self.assertIsInstance(history_record, dict)
        self.assertEqual(history_record["version_number"], 2)
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.service.TracerContextManager')
    @patch('PersistenceService.service.logger')
    def test_get_latest_task_history_not_found(self, mock_logger, mock_tracer):
        """Test getting the latest task history record through the service when it doesn't exist."""
        # Mock the task history repository
        self.persistence_service.task_history_repo.get_latest_task_history.return_value = None
        
        # Call the method
        history_record = self.persistence_service.get_latest_task_history(UUID('123e4567-e89b-12d3-a456-426614174001'))
        
        # Assertions
        self.assertIsNone(history_record)
        mock_logger.info.assert_called()

if __name__ == '__main__':
    unittest.main()