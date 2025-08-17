"""
Test module for ToolService
"""

import unittest
from interfaces import ToolCallRequest
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