from typing import List, Dict, Any, Optional
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .interfaces import OpenAICompatibleTool
from interfaces.interfaces import AgentResult


class ToolAdapter:
    """工具适配器，用于将AgentResult中的工具定义转换为OpenAI兼容格式"""
    
    @staticmethod
    def adapt_tools_for_supported_model(agent_result: AgentResult) -> List[OpenAICompatibleTool]:
        """
        为支持原生Tool Calling的模型适配工具
        
        Args:
            agent_result: AgentResult对象，包含工具调用请求
            
        Returns:
            List[OpenAICompatibleTool]: OpenAI兼容的工具列表
        """
        if not agent_result.output or not hasattr(agent_result.output, 'intent'):
            return []
            
        intent = agent_result.output.intent
        
        # 检查是否为工具调用请求
        if not hasattr(intent, 'tool_id'):
            return []
            
        # 将工具调用请求转换为OpenAI格式
        tools = []
        
        # 如果intent是ToolCallRequest列表
        if isinstance(intent, list):
            for tool_call_request in intent:
                if hasattr(tool_call_request, 'tool_id'):
                    tool = ToolAdapter._convert_tool_call_request(tool_call_request)
                    if tool:
                        tools.append(tool)
        # 如果intent是单个ToolCallRequest
        elif hasattr(intent, 'tool_id'):
            tool = ToolAdapter._convert_tool_call_request(intent)
            if tool:
                tools.append(tool)
                
        return tools
        
    @staticmethod
    def adapt_tools_for_unsupported_model(agent_result: AgentResult) -> str:
        """
        为不支持Tool Calling的模型适配工具（模拟实现）
        
        Args:
            agent_result: AgentResult对象，包含工具调用请求
            
        Returns:
            str: 渲染成文本的工具列表
        """
        if not agent_result.output or not hasattr(agent_result.output, 'intent'):
            return ""
            
        intent = agent_result.output.intent
        
        # 检查是否为工具调用请求
        if not hasattr(intent, 'tool_id'):
            return ""
            
        # 将工具调用请求渲染成文本
        tools_text = "可用工具列表:\n"
        
        # 如果intent是ToolCallRequest列表
        if isinstance(intent, list):
            for i, tool_call_request in enumerate(intent, 1):
                if hasattr(tool_call_request, 'tool_id'):
                    tools_text += f"{i}. {ToolAdapter._render_tool_call_request(tool_call_request)}\n"
        # 如果intent是单个ToolCallRequest
        elif hasattr(intent, 'tool_id'):
            tools_text += f"1. {ToolAdapter._render_tool_call_request(intent)}\n"
            
        tools_text += "\n请根据需要选择合适的工具调用。"
        return tools_text
        
    @staticmethod
    def _convert_tool_call_request(tool_call_request) -> Optional[OpenAICompatibleTool]:
        """
        将单个ToolCallRequest转换为OpenAICompatibleTool
        
        Args:
            tool_call_request: ToolCallRequest对象
            
        Returns:
            Optional[OpenAICompatibleTool]: OpenAI兼容的工具对象
        """
        try:
            # 构建函数定义
            function_def = {
                "name": tool_call_request.tool_id,
                "arguments": tool_call_request.arguments
            }
            
            # 创建OpenAI兼容的工具对象
            tool = OpenAICompatibleTool(
                type="function",
                function=function_def
            )
            
            return tool
        except Exception:
            # 转换失败时返回None
            return None
            
    @staticmethod
    def _render_tool_call_request(tool_call_request) -> str:
        """
        将单个ToolCallRequest渲染成文本
        
        Args:
            tool_call_request: ToolCallRequest对象
            
        Returns:
            str: 渲染后的文本
        """
        try:
            # 构建工具调用的文本表示
            arguments_str = ", ".join([f"{k}={v}" for k, v in tool_call_request.arguments.items()])
            return f"{tool_call_request.tool_id}({arguments_str})"
        except Exception:
            # 渲染失败时返回空字符串
            return ""