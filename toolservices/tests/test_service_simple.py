"""
ToolService Test Module (Simplified Version)

This version removes LoggingService dependencies for simpler testing.
"""

import unittest
import sys
import os

# Add project root to path
sys.path.insert(0, '/root/projects/atom_agents')

from interfaces import ToolCallRequest, ToolResult


class MockLogger:
    """Mock logger for testing."""
    def info(self, msg, extra=None):
        pass
    
    def error(self, msg, extra=None):
        pass


class MockTracerContextManager:
    """Mock tracer for testing."""
    @staticmethod
    def start_span(name):
        from contextlib import nullcontext
        return nullcontext()


# Mock the LoggingService
import toolservices.service
import toolservices.core.loader
import toolservices.core.validator
import toolservices.core.executor

toolservices.service.logger = MockLogger()
toolservices.core.loader.logger = MockLogger()
toolservices.core.validator.logger = MockLogger()
toolservices.core.executor.logger = MockLogger()
toolservices.service.TracerContextManager = MockTracerContextManager()
toolservices.core.loader.TracerContextManager = MockTracerContextManager()
toolservices.core.validator.TracerContextManager = MockTracerContextManager()
toolservices.core.executor.TracerContextManager = MockTracerContextManager()


from toolservices.service import ToolService


class TestToolService(unittest.TestCase):
    """Test cases for ToolService."""

    def setUp(self):
        """Set up test fixtures."""
        self.tool_service = ToolService()

    def test_hello_tool_success(self):
        """Test successful execution of hello tool."""
        # Arrange
        request = ToolCallRequest(
            tool_id="TestTools.hello",
            arguments={"name": "World"}
        )

        # Act
        result = self.tool_service.run_tool(request)

        # Assert
        self.assertEqual(result.status, "SUCCESS")
        self.assertIsNotNone(result.output)
        self.assertIn("message", result.output)
        self.assertIn("World", result.output["message"])

    def test_calculator_tool_success(self):
        """Test successful execution of calculator tool."""
        # Arrange
        request = ToolCallRequest(
            tool_id="TestTools.calculator",
            arguments={"operation": "add", "a": 5, "b": 3}
        )

        # Act
        result = self.tool_service.run_tool(request)

        # Assert
        self.assertEqual(result.status, "SUCCESS")
        self.assertIsNotNone(result.output)
        self.assertEqual(result.output["result"], 8)

    def test_tool_not_found(self):
        """Test execution of non-existent tool."""
        # Arrange
        request = ToolCallRequest(
            tool_id="NonExistentTool.test",
            arguments={}
        )

        # Act
        result = self.tool_service.run_tool(request)

        # Assert
        self.assertEqual(result.status, "FAILURE")
        self.assertEqual(result.error_type, "TOOL_NOT_FOUND")

    def test_validation_error(self):
        """Test execution with invalid arguments."""
        # Arrange
        request = ToolCallRequest(
            tool_id="TestTools.hello",
            arguments={}  # Missing required "name" parameter
        )

        # Act
        result = self.tool_service.run_tool(request)

        # Assert
        self.assertEqual(result.status, "FAILURE")
        self.assertEqual(result.error_type, "VALIDATION_ERROR")

    def test_tool_execution_error(self):
        """Test execution of tool that raises an exception."""
        # Arrange
        request = ToolCallRequest(
            tool_id="TestTools.failing",
            arguments={"message": "Test error message"}
        )

        # Act
        result = self.tool_service.run_tool(request)

        # Assert
        self.assertEqual(result.status, "FAILURE")
        self.assertEqual(result.error_type, "TOOL_EXECUTION_ERROR")
        self.assertIn("Test error message", result.error_message)


if __name__ == "__main__":
    unittest.main()