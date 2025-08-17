"""
Test Tools for ToolService

These are simple test tools used for testing the ToolService functionality.
"""

from typing import Dict, Any


def hello_tool(name: str) -> Dict[str, Any]:
    """
    A simple test tool that returns a greeting.
    
    Args:
        name: The name to greet
        
    Returns:
        A dictionary with greeting message
    """
    return {
        "message": f"Hello, {name}!",
        "tool": "hello_tool"
    }


def calculator_tool(operation: str, a: float, b: float) -> Dict[str, Any]:
    """
    A simple calculator tool.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: First operand
        b: Second operand
        
    Returns:
        A dictionary with the result
    """
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")
    
    return {
        "operation": operation,
        "operand_a": a,
        "operand_b": b,
        "result": result
    }


def failing_tool(message: str) -> Dict[str, Any]:
    """
    A test tool that always fails.
    
    Args:
        message: Error message to raise
        
    Raises:
        Exception: Always raises an exception with the provided message
    """
    raise Exception(message)