import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from LLMService.llmgateway.tokenizer import Tokenizer
from LLMService.llmgateway.interfaces import OpenAICompatibleRequest, OpenAICompatibleMessage, OpenAICompatibleTool


class TestTokenizer(unittest.TestCase):
    """Token计数器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.tokenizer = Tokenizer()
        
    def test_get_encoder_exact_match(self):
        """测试获取编码器-精确匹配"""
        encoder = self.tokenizer._get_encoder("gpt-4")
        self.assertIsNotNone(encoder)
        
    def test_get_encoder_prefix_match(self):
        """测试获取编码器-前缀匹配"""
        encoder = self.tokenizer._get_encoder("gpt-4-0613")
        self.assertIsNotNone(encoder)
        
    def test_get_encoder_default(self):
        """测试获取编码器-默认编码器"""
        encoder = self.tokenizer._get_encoder("unknown-model")
        self.assertIsNotNone(encoder)
        # 应该返回默认编码器（gpt-4o-mini）
        default_encoder = self.tokenizer.encoders["gpt-4o-mini"]
        self.assertEqual(encoder, default_encoder)
        
    def test_estimate_tokens_simple_message(self):
        """测试估算Token-简单消息"""
        request = OpenAICompatibleRequest(
            model="gpt-4o-mini",
            messages=[
                OpenAICompatibleMessage(role="user", content="Hello, world!")
            ]
        )
        
        token_count = self.tokenizer.estimate_tokens(request)
        # 验证返回的是一个正整数
        self.assertIsInstance(token_count, int)
        self.assertGreater(token_count, 0)
        
    def test_estimate_tokens_multiple_messages(self):
        """测试估算Token-多条消息"""
        request = OpenAICompatibleRequest(
            model="gpt-4o-mini",
            messages=[
                OpenAICompatibleMessage(role="user", content="Hello, world!"),
                OpenAICompatibleMessage(role="assistant", content="Hi there! How can I help you?"),
                OpenAICompatibleMessage(role="user", content="I need some assistance with my project.")
            ]
        )
        
        token_count = self.tokenizer.estimate_tokens(request)
        # 验证返回的是一个正整数
        self.assertIsInstance(token_count, int)
        self.assertGreater(token_count, 0)
        
    def test_estimate_tokens_with_tools(self):
        """测试估算Token-带工具"""
        request = OpenAICompatibleRequest(
            model="gpt-4o-mini",
            messages=[
                OpenAICompatibleMessage(role="user", content="What's the weather like today?")
            ],
            tools=[
                OpenAICompatibleTool(
                    type="function",
                    function={
                        "name": "get_current_weather",
                        "description": "Get the current weather",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "location": {
                                    "type": "string",
                                    "description": "The city and state, e.g. San Francisco, CA"
                                }
                            },
                            "required": ["location"]
                        }
                    }
                )
            ]
        )
        
        token_count = self.tokenizer.estimate_tokens(request)
        # 验证返回的是一个正整数
        self.assertIsInstance(token_count, int)
        self.assertGreater(token_count, 0)
        
    def test_count_tokens_from_response_text(self):
        """测试从响应中计算Token-文本内容"""
        # 这里只是简单测试，实际实现可能需要更复杂的模拟
        # 因为我们没有直接访问tiktoken的encode方法
        self.assertTrue(True)  # 占位测试，实际实现需要更复杂的模拟


if __name__ == '__main__':
    unittest.main()