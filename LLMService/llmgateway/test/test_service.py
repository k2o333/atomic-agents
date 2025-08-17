import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from LLMService.llmgateway.service import LLMGatewayService
from LLMService.llmgateway.interfaces import OpenAICompatibleRequest, OpenAICompatibleMessage


class TestLLMGatewayService(unittest.TestCase):
    """LLM网关服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 使用patch模拟配置和HTTP客户端
        self.config_patch = patch('LLMService.llmgateway.service.LLMConfig')
        self.http_client_patch = patch('LLMService.llmgateway.service.httpx.AsyncClient')
        self.tokenizer_patch = patch('LLMService.llmgateway.service.Tokenizer')
        
        self.mock_config = self.config_patch.start()
        self.mock_http_client = self.http_client_patch.start()
        self.mock_tokenizer = self.tokenizer_patch.start()
        
        # 配置模拟对象
        self.mock_config_instance = MagicMock()
        self.mock_config_instance.validate.return_value = True
        self.mock_config_instance.get_openai_config.return_value = {
            'api_key': 'test-key',
            'base_url': 'https://api.openai.com/v1'
        }
        self.mock_config.return_value = self.mock_config_instance
        
        self.mock_http_client_instance = AsyncMock()
        self.mock_http_client.return_value = self.mock_http_client_instance
        
        self.mock_tokenizer_instance = MagicMock()
        self.mock_tokenizer_instance.estimate_tokens.return_value = 100
        self.mock_tokenizer_instance.count_tokens_from_response.return_value = 50
        self.mock_tokenizer.return_value = self.mock_tokenizer_instance
        
    def tearDown(self):
        """测试后清理"""
        self.config_patch.stop()
        self.http_client_patch.stop()
        self.tokenizer_patch.stop()
        
    def test_init_success(self):
        """测试初始化成功"""
        # 创建服务实例
        service = LLMGatewayService()
        
        # 验证配置验证被调用
        self.mock_config_instance.validate.assert_called_once()
        
        # 验证HTTP客户端被正确初始化
        self.mock_http_client.assert_called_once_with(
            base_url='https://api.openai.com/v1',
            headers={
                'Authorization': 'Bearer test-key',
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
        
    def test_init_config_validation_failed(self):
        """测试初始化时配置验证失败"""
        # 配置模拟对象返回验证失败
        self.mock_config_instance.validate.return_value = False
        
        # 验证初始化时抛出ValueError
        with self.assertRaises(ValueError) as context:
            LLMGatewayService()
            
        self.assertEqual(str(context.exception), "LLM配置验证失败")
        
    async def test_chat_completion_success(self):
        """测试聊天补全成功"""
        # 创建服务实例
        service = LLMGatewayService()
        
        # 创建测试请求
        request = OpenAICompatibleRequest(
            model="gpt-4o-mini",
            messages=[
                OpenAICompatibleMessage(role="user", content="Hello, world!")
            ]
        )
        
        # 配置模拟响应
        mock_response_data = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,  # 将被服务覆盖
                "completion_tokens": 0,  # 将被服务覆盖
                "total_tokens": 0  # 将被服务覆盖
            }
        }
        self.mock_http_client_instance.post.return_value = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value=mock_response_data)
        )
        
        # 调用聊天补全方法
        response = await service.chat_completion(request)
        
        # 验证Token计数方法被调用
        self.mock_tokenizer_instance.estimate_tokens.assert_called_once_with(request)
        self.mock_tokenizer_instance.count_tokens_from_response.assert_called_once_with(response)
        
        # 验证响应数据正确
        self.assertEqual(response.id, "test-id")
        self.assertEqual(response.object, "chat.completion")
        self.assertEqual(response.model, "gpt-4o-mini")
        self.assertEqual(response.choices[0]["message"]["content"], "Hello! How can I help you today?")
        
        # 验证Token使用量被正确设置
        self.assertEqual(response.usage.prompt_tokens, 100)
        self.assertEqual(response.usage.completion_tokens, 50)
        self.assertEqual(response.usage.total_tokens, 150)
        
    async def test_call_openai_api_success(self):
        """测试调用OpenAI API成功"""
        # 创建服务实例
        service = LLMGatewayService()
        
        # 创建测试请求
        request = OpenAICompatibleRequest(
            model="gpt-4o-mini",
            messages=[
                OpenAICompatibleMessage(role="user", content="Hello, world!")
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        # 配置模拟响应
        mock_response_data = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-4o-mini",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you today?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
        mock_response = AsyncMock(
            status_code=200,
            json=AsyncMock(return_value=mock_response_data)
        )
        mock_response.raise_for_status = MagicMock()
        self.mock_http_client_instance.post.return_value = mock_response
        
        # 调用内部API调用方法
        response_data = await service._call_openai_api(request)
        
        # 验证HTTP请求被正确发送
        expected_payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, world!"
                }
            ],
            "stream": False,
            "temperature": 0.7,
            "max_tokens": 100
        }
        self.mock_http_client_instance.post.assert_called_once_with("/chat/completions", json=expected_payload)
        
        # 验证响应数据正确
        self.assertEqual(response_data, mock_response_data)
        
    async def test_call_openai_api_http_error(self):
        """测试调用OpenAI API时HTTP错误"""
        # 创建服务实例
        service = LLMGatewayService()
        
        # 创建测试请求
        request = OpenAICompatibleRequest(
            model="gpt-4o-mini",
            messages=[
                OpenAICompatibleMessage(role="user", content="Hello, world!")
            ]
        )
        
        # 配置模拟HTTP错误
        mock_response = AsyncMock(
            status_code=429,
            text="Rate limit exceeded"
        )
        http_error = Exception("429: Rate limit exceeded")
        mock_response.raise_for_status.side_effect = http_error
        self.mock_http_client_instance.post.return_value = mock_response
        
        # 验证调用时抛出异常
        with self.assertRaises(Exception) as context:
            await service._call_openai_api(request)
            
        self.assertIn("429: Rate limit exceeded", str(context.exception))


if __name__ == '__main__':
    unittest.main()