"""
Unit tests for EdgeRepository
"""

import unittest
from unittest.mock import Mock, patch
from uuid import UUID
from datetime import datetime

from PersistenceService.repository.edge_repository import EdgeRepository
from PersistenceService.models.edge import EdgeRecord

class TestEdgeRepository(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_db_manager = Mock()
        self.edge_repo = EdgeRepository(self.mock_db_manager)
    
    @patch('PersistenceService.repository.edge_repository.TracerContextManager')
    @patch('PersistenceService.repository.edge_repository.logger')
    def test_create_edge(self, mock_logger, mock_tracer):
        """Test creating a new edge."""
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
        edge_id = self.edge_repo.create_edge(
            workflow_id=UUID('123e4567-e89b-12d3-a456-426614174001'),
            source_task_id=UUID('123e4567-e89b-12d3-a456-426614174002'),
            target_task_id=UUID('123e4567-e89b-12d3-a456-426614174003'),
            condition={"evaluator": "CEL", "expression": "result.success == true"}
        )
        
        # Assertions
        self.assertEqual(edge_id, UUID('123e4567-e89b-12d3-a456-426614174000'))
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()
    
    @patch('PersistenceService.repository.edge_repository.TracerContextManager')
    @patch('PersistenceService.repository.edge_repository.logger')
    def test_get_outgoing_edges(self, mock_logger, mock_tracer):
        """Test getting outgoing edges for a task."""
        # Mock the database connection and cursor
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_db_session = Mock()
        mock_db_session.__enter__.return_value = mock_conn
        self.mock_db_manager.get_db_session.return_value = mock_db_session
        
        # Mock the cursor execute and fetchall
        mock_cursor.fetchall.return_value = [
            (
                UUID('123e4567-e89b-12d3-a456-426614174000'),
                UUID('123e4567-e89b-12d3-a456-426614174001'),
                UUID('123e4567-e89b-12d3-a456-426614174002'),
                UUID('123e4567-e89b-12d3-a456-426614174003'),
                {"evaluator": "CEL", "expression": "result.success == true"},
                {"mappings": {"output": "input"}},
                datetime.now()
            )
        ]
        
        # Call the method
        edges = self.edge_repo.get_outgoing_edges(UUID('123e4567-e89b-12d3-a456-426614174002'))
        
        # Assertions
        self.assertEqual(len(edges), 1)
        self.assertIsInstance(edges[0], EdgeRecord)
        self.assertEqual(edges[0].id, UUID('123e4567-e89b-12d3-a456-426614174000'))
        mock_cursor.execute.assert_called_once()
        mock_logger.info.assert_called()

if __name__ == '__main__':
    unittest.main()