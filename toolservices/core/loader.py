"""
Tool Loader

This module provides functionality to dynamically load tool functions
from their implementation paths.
"""

import importlib
from typing import Callable, Any
from LoggingService.sdk import get_logger

logger = get_logger(__name__)


class ToolLoader:
    """Tool loader for dynamically importing tool functions."""
    
    @staticmethod
    def load_tool_function(implementation_path: str) -> Callable[..., Any]:
        """
        动态加载Tool函数。
        
        Args:
            implementation_path: Tool函数的完整路径，格式为"module.submodule.function"
            
        Returns:
            可调用的函数对象
            
        Raises:
            ImportError: 当无法导入模块时
            AttributeError: 当模块中找不到指定函数时
        """
        logger.info("Loading tool function", extra={"implementation_path": implementation_path})
        
        try:
            # 分离模块路径和函数名
            module_path, function_name = implementation_path.rsplit('.', 1)
            
            # 动态导入模块
            module = importlib.import_module(module_path)
            
            # 获取函数
            func = getattr(module, function_name)
            
            logger.info("Tool function loaded successfully", extra={
                "implementation_path": implementation_path,
                "module": module_path,
                "function": function_name
            })
            
            return func
            
        except ValueError as e:
            logger.error("Invalid implementation path format", extra={
                "implementation_path": implementation_path,
                "error": str(e)
            })
            raise ImportError(f"Invalid implementation path format: {implementation_path}") from e
            
        except ImportError as e:
            logger.error("Failed to import module", extra={
                "module_path": module_path,
                "error": str(e)
            })
            raise ImportError(f"Failed to import module '{module_path}': {str(e)}") from e
            
        except AttributeError as e:
            logger.error("Function not found in module", extra={
                "module_path": module_path,
                "function_name": function_name,
                "error": str(e)
            })
            raise AttributeError(f"Function '{function_name}' not found in module '{module_path}'") from e