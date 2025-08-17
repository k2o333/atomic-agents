"""
Example usage of ToolService
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/root/projects/atom_agents')

from interfaces import ToolCallRequest
from toolservices.service import ToolService


def main():
    """Main function to demonstrate ToolService usage."""
    print("ToolService Example")
    print("=" * 20)
    
    # Create ToolService instance
    tool_service = ToolService()
    
    # Example 1: Successful tool execution
    print("\n1. Executing hello tool:")
    request = ToolCallRequest(
        tool_id="TestTools.hello",
        arguments={"name": "Alice"}
    )
    result = tool_service.run_tool(request)
    print(f"Status: {result.status}")
    if result.status == "SUCCESS":
        print(f"Output: {result.output}")
    else:
        print(f"Error: {result.error_message}")
    
    # Example 2: Calculator tool
    print("\n2. Executing calculator tool:")
    request = ToolCallRequest(
        tool_id="TestTools.calculator",
        arguments={"operation": "multiply", "a": 6, "b": 7}
    )
    result = tool_service.run_tool(request)
    print(f"Status: {result.status}")
    if result.status == "SUCCESS":
        print(f"Output: {result.output}")
        print(f"Result: {result.output['result']}")
    else:
        print(f"Error: {result.error_message}")
    
    # Example 3: Tool not found
    print("\n3. Executing non-existent tool:")
    request = ToolCallRequest(
        tool_id="NonExistentTool.test",
        arguments={}
    )
    result = tool_service.run_tool(request)
    print(f"Status: {result.status}")
    if result.status == "FAILURE":
        print(f"Error Type: {result.error_type}")
        print(f"Error Message: {result.error_message}")
    
    # Example 4: Validation error
    print("\n4. Executing tool with invalid arguments:")
    request = ToolCallRequest(
        tool_id="TestTools.hello",
        arguments={}  # Missing required "name" parameter
    )
    result = tool_service.run_tool(request)
    print(f"Status: {result.status}")
    if result.status == "FAILURE":
        print(f"Error Type: {result.error_type}")
        print(f"Error Message: {result.error_message}")
    
    # Example 5: Tool execution error
    print("\n5. Executing failing tool:")
    request = ToolCallRequest(
        tool_id="TestTools.failing",
        arguments={"message": "Something went wrong!"}
    )
    result = tool_service.run_tool(request)
    print(f"Status: {result.status}")
    if result.status == "FAILURE":
        print(f"Error Type: {result.error_type}")
        print(f"Error Message: {result.error_message}")


if __name__ == "__main__":
    main()