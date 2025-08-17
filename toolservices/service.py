"""
Tool Service Main Interface

This module provides the main service interface for the Tool Service,
implementing the core run_tool method that other modules will use.
"""

from typing import Dict, Any, Optional
from interfaces import ToolCallRequest, ToolResult
from .core.executor import ToolExecutor
from .core.validator import validate_arguments
from LoggingService.sdk import get_logger, TracerContextManager

# Initialize logger
logger = get_logger(__name__)


class ToolService:
    """Main service class for the Tool Service."""

    def __init__(self):
        self.executor = ToolExecutor()
    
    def run_tool(self, tool_call_request: ToolCallRequest) -> ToolResult:
        """
        根据ToolCallRequest，动态加载、校验并执行一个Tool。
        
        Args:
            tool_call_request: ToolCallRequest对象，包含tool_id和arguments
            
        Returns:
            ToolResult: 包含执行结果的标准化结果对象
        """
        with TracerContextManager.start_span(f"tool_execution:{tool_call_request.tool_id}"):
            logger.info("Running tool", extra={
                "tool_id": tool_call_request.tool_id,
                "arguments": tool_call_request.arguments
            })
            
            try:
                # 1. 获取Tool定义（从能力注册表）
                tool_definition = self._get_tool_definition(tool_call_request.tool_id)
                if not tool_definition:
                    return ToolResult(
                        status="FAILURE",
                        error_type="TOOL_NOT_FOUND",
                        error_message=f"Tool with id '{tool_call_request.tool_id}' not found in capability registry"
                    )
                
                # 2. 参数校验
                validation_result = validate_arguments(
                    tool_call_request.arguments,
                    tool_definition.get("parameters_schema", {})
                )
                if not validation_result.is_valid:
                    return ToolResult(
                        status="FAILURE",
                        error_type="VALIDATION_ERROR",
                        error_message=f"Argument validation failed: {validation_result.error_message}"
                    )
                
                # 3. 执行Tool
                result = self.executor.execute_tool(
                    tool_definition["implementation_path"],
                    tool_call_request.arguments
                )
                
                # 4. 返回结果
                return result
                
            except Exception as e:
                logger.error("Tool execution failed", extra={
                    "tool_id": tool_call_request.tool_id,
                    "error": str(e)
                })
                return ToolResult(
                    status="FAILURE",
                    error_type="TOOL_EXECUTION_ERROR",
                    error_message=str(e)
                )
    
    def _get_tool_definition(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """
        从能力注册表获取Tool定义。
        
        Args:
            tool_id: Tool的唯一标识符
            
        Returns:
            Tool定义字典，如果未找到则返回None
        """
        # TODO: 实际实现中应该从PersistenceService或能力注册表中获取
        # 这里是简化的实现，用于演示
        
        # 模拟从capabilities.json中读取
        import json
        import os
        
        capabilities_file = "/root/projects/atom_agents/capabilities.json"
        if not os.path.exists(capabilities_file):
            logger.error("Capabilities file not found", extra={"file": capabilities_file})
            return None
            
        try:
            with open(capabilities_file, 'r', encoding='utf-8') as f:
                capabilities = json.load(f)
            
            tools = capabilities.get("registries", {}).get("tools", [])
            for tool in tools:
                if tool.get("id") == tool_id:
                    return tool
                    
            return None
        except Exception as e:
            logger.error("Failed to load capabilities", extra={"error": str(e)})
            return None