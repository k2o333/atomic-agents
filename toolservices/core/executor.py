"""
Tool Executor

This module provides functionality to execute tool functions with
proper error handling and result formatting.
"""

from typing import Dict, Any, Callable
from interfaces import ToolResult
from .loader import ToolLoader
from LoggingService.sdk import get_logger

logger = get_logger(__name__)


class ToolExecutor:
    """Tool executor for running tool functions."""
    
    def __init__(self):
        self.loader = ToolLoader()
    
    def execute_tool(self, implementation_path: str, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行Tool函数。
        
        Args:
            implementation_path: Tool函数的完整路径
            arguments: 传递给Tool函数的参数
            
        Returns:
            ToolResult: 执行结果
        """
        logger.info("Executing tool", extra={
            "implementation_path": implementation_path,
            "arguments_keys": list(arguments.keys())
        })
        
        try:
            # 1. 动态加载函数
            func = self.loader.load_tool_function(implementation_path)
            
            # 2. 执行函数
            result = func(**arguments)
            
            # 3. 格式化结果
            if isinstance(result, dict) and "status" in result:
                # 如果Tool已经返回了标准化的结果格式
                logger.info("Tool returned standardized result", extra={"status": result.get("status")})
                return ToolResult(**result)
            else:
                # 否则包装成成功结果
                logger.info("Tool executed successfully")
                return ToolResult(
                    status="SUCCESS",
                    output=result
                )
                
        except Exception as e:
            logger.error("Tool execution failed", extra={
                "implementation_path": implementation_path,
                "error": str(e)
            })
            return ToolResult(
                status="FAILURE",
                error_type="TOOL_EXECUTION_ERROR",
                error_message=str(e)
            )