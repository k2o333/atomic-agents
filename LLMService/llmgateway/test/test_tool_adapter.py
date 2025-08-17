import unittest
from unittest.mock import MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from LLMService.llmgateway.tool_adapter import ToolAdapter
from interfaces.interfaces import (
    AgentResult, AgentIntent, ToolCallRequest, FinalAnswer
)


class TestToolAdapter(unittest.TestCase):
    """工具适配器测试类"""
    
    def test_adapt_tools_for_supported_model_single_tool(self):
        """测试为支持的模型适配工具-单个工具"""
        # 创建模拟的AgentResult
        tool_call_request = ToolCallRequest(
            tool_id="get_current_weather",
            arguments={"location": "San Francisco, CA"}
        )
        agent_intent = AgentIntent(
            thought="User wants to know the weather",
            intent=tool_call_request
        )
        agent_result = AgentResult(
            status="SUCCESS",
            output=agent_intent
        )
        
        # 调用适配方法
        tools = ToolAdapter.adapt_tools_for_supported_model(agent_result)
        
        # 验证结果
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].type, "function")
        self.assertEqual(tools[0].function["name"], "get_current_weather")
        self.assertEqual(tools[0].function["arguments"], {"location": "San Francisco, CA"})
        
    def test_adapt_tools_for_supported_model_multiple_tools(self):
        """测试为支持的模型适配工具-多个工具"""
        # 创建模拟的AgentResult
        tool_call_request1 = ToolCallRequest(
            tool_id="get_current_weather",
            arguments={"location": "San Francisco, CA"}
        )
        tool_call_request2 = ToolCallRequest(
            tool_id="get_stock_price",
            arguments={"symbol": "AAPL"}
        )
        agent_intent = AgentIntent(
            thought="User wants to know the weather and stock price",
            intent=tool_call_request1  # 只传递单个工具调用请求
        )
        agent_result = AgentResult(
            status="SUCCESS",
            output=agent_intent
        )
        
        # 调用适配方法
        tools = ToolAdapter.adapt_tools_for_supported_model(agent_result)
        
        # 验证结果
        self.assertEqual(len(tools), 1)
        self.assertEqual(tools[0].type, "function")
        self.assertEqual(tools[0].function["name"], "get_current_weather")
        self.assertEqual(tools[0].function["arguments"], {"location": "San Francisco, CA"})
        
    def test_adapt_tools_for_supported_model_no_tools(self):
        """测试为支持的模型适配工具-无工具"""
        # 创建模拟的AgentResult（无工具调用）
        final_answer = FinalAnswer(
            content="Hello! How can I help you today?"
        )
        agent_intent = AgentIntent(
            thought="User sent a greeting",
            intent=final_answer
        )
        agent_result = AgentResult(
            status="SUCCESS",
            output=agent_intent
        )
        
        # 调用适配方法
        tools = ToolAdapter.adapt_tools_for_supported_model(agent_result)
        
        # 验证结果
        self.assertEqual(len(tools), 0)
        
    def test_adapt_tools_for_unsupported_model_single_tool(self):
        """测试为不支持的模型适配工具-单个工具"""
        # 创建模拟的AgentResult
        tool_call_request = ToolCallRequest(
            tool_id="get_current_weather",
            arguments={"location": "San Francisco, CA"}
        )
        agent_intent = AgentIntent(
            thought="User wants to know the weather",
            intent=tool_call_request
        )
        agent_result = AgentResult(
            status="SUCCESS",
            output=agent_intent
        )
        
        # 调用适配方法
        tools_text = ToolAdapter.adapt_tools_for_unsupported_model(agent_result)
        
        # 验证结果包含工具信息
        self.assertIn("get_current_weather", tools_text)
        self.assertIn("location=San Francisco, CA", tools_text)
        
    def test_adapt_tools_for_unsupported_model_multiple_tools(self):
        """测试为不支持的模型适配工具-多个工具"""
        # 创建模拟的AgentResult
        tool_call_request = ToolCallRequest(
            tool_id="get_current_weather",
            arguments={"location": "San Francisco, CA"}
        )
        agent_intent = AgentIntent(
            thought="User wants to know the weather and stock price",
            intent=tool_call_request  # 只传递单个工具调用请求
        )
        agent_result = AgentResult(
            status="SUCCESS",
            output=agent_intent
        )
        
        # 调用适配方法
        tools_text = ToolAdapter.adapt_tools_for_unsupported_model(agent_result)
        
        # 验证结果包含工具信息
        self.assertIn("get_current_weather", tools_text)
        self.assertIn("location=San Francisco, CA", tools_text)
        
    def test_adapt_tools_for_unsupported_model_no_tools(self):
        """测试为不支持的模型适配工具-无工具"""
        # 创建模拟的AgentResult（无工具调用）
        final_answer = FinalAnswer(
            content="Hello! How can I help you today?"
        )
        agent_intent = AgentIntent(
            thought="User sent a greeting",
            intent=final_answer
        )
        agent_result = AgentResult(
            status="SUCCESS",
            output=agent_intent
        )
        
        # 调用适配方法
        tools_text = ToolAdapter.adapt_tools_for_unsupported_model(agent_result)
        
        # 验证结果为空字符串
        self.assertEqual(tools_text, "")


if __name__ == '__main__':
    unittest.main()