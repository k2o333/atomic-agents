import unittest
import sys
import os
import uuid

# Add the LoggingService directory to the path so we can import from it
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sdk import TracerContextManager, get_logger, _trace_id_ctx, _span_id_ctx, inject_trace_context, extract_trace_context, generate_id
import logging
import io
import json

class TestLoggingService(unittest.TestCase):

    def setUp(self):
        # Create a logger for testing
        self.logger = get_logger("test_logger")
        # Suppress console output for tests
        self.log_stream = io.StringIO()
        handler = logging.StreamHandler(self.log_stream)
        formatter = self.logger.handlers[0].formatter # Reuse the TraceInjectingJsonFormatter
        handler.setFormatter(formatter)
        self.logger.handlers = [handler] # Replace handlers with our stream handler
        self.logger.setLevel(logging.INFO)

    def test_get_logger_returns_logger(self):
        self.assertIsInstance(self.logger, logging.Logger)

    def test_logger_outputs_json(self):
        self.logger.info("Test message")
        log_output = self.log_stream.getvalue().strip()
        try:
            log_data = json.loads(log_output)
            self.assertIn("message", log_data)
            self.assertEqual(log_data["message"], "Test message")
        except json.JSONDecodeError:
            self.fail("Logger output is not valid JSON")

    def test_trace_id_injection(self):
        trace_id = generate_id() # 使用符合格式的ID
        # Set a trace ID in the context
        token = _trace_id_ctx.set(trace_id)
        
        self.logger.info("Message with trace ID")
        log_output = self.log_stream.getvalue().strip()
        _trace_id_ctx.reset(token) # Clean up context
        
        try:
            log_data = json.loads(log_output)
            self.assertIn("trace_id", log_data)
            self.assertEqual(log_data["trace_id"], trace_id)
        except json.JSONDecodeError:
            self.fail("Logger output is not valid JSON")

    def test_span_id_injection(self):
        span_id = generate_id() # 使用符合格式的ID
        # Set a span ID in the context
        token = _span_id_ctx.set(span_id)
        
        self.logger.info("Message with span ID")
        log_output = self.log_stream.getvalue().strip()
        _span_id_ctx.reset(token) # Clean up context
        
        try:
            log_data = json.loads(log_output)
            self.assertIn("span_id", log_data)
            self.assertEqual(log_data["span_id"], span_id)
        except json.JSONDecodeError:
            self.fail("Logger output is not valid JSON")

    def test_start_trace_context_manager(self):
        trace_name = "test_trace"
        with TracerContextManager.start_trace(trace_name):
            current_trace_id = _trace_id_ctx.get()
            current_span_id = _span_id_ctx.get() # Root span ID
            self.assertIsNotNone(current_trace_id)
            self.assertIsNotNone(current_span_id)
            # They might be the same or related in our simple implementation
            # Just assert they exist for now.
            self.logger.info("Inside trace")
        
        # After the context manager, the context should be cleared or reset
        # Since we are not managing a stack, we check if it's empty or raises LookupError
        # In our implementation, default value is None, so get() returns None after reset
        self.assertIsNone(_trace_id_ctx.get())
        self.assertIsNone(_span_id_ctx.get())

    def test_start_span_context_manager(self):
        trace_name = "test_trace_for_span"
        span_name = "test_span"
        
        with TracerContextManager.start_trace(trace_name):
            trace_id_during_trace = _trace_id_ctx.get()
            
            with TracerContextManager.start_span(span_name):
                span_id_during_span = _span_id_ctx.get()
                parent_span_id = _span_id_ctx.get() # In our simple case, it's the root
                self.assertIsNotNone(span_id_during_span)
                # Log inside span to check IDs
                self.logger.info("Inside span")
            
            # After span ends, span_id should be reset to the root (trace_id) or cleared
            # In our simple implementation, it's reset to the trace_id (which was the root span id)
            self.assertEqual(_span_id_ctx.get(), trace_id_during_trace)
        
        # After trace ends, context should be cleared
        self.assertIsNone(_trace_id_ctx.get())
        self.assertIsNone(_span_id_ctx.get())
        
    def test_inject_trace_context(self):
        trace_id = generate_id() # 使用符合格式的ID
        span_id = generate_id() # 使用符合格式的ID
        
        token_t = _trace_id_ctx.set(trace_id)
        token_s = _span_id_ctx.set(span_id)
        
        context_dict = inject_trace_context()
        
        _trace_id_ctx.reset(token_t)
        _span_id_ctx.reset(token_s)
        
        self.assertIn("traceparent", context_dict)
        traceparent = context_dict["traceparent"]
        self.assertTrue(traceparent.startswith(f"00-{trace_id}-{span_id}"))
        
    def test_extract_trace_context(self):
        trace_id = generate_id() # 使用符合格式的ID
        span_id = generate_id() # 使用符合格式的ID
        context_dict = {"traceparent": f"00-{trace_id}-{span_id}-01"}
        
        # Ensure context is clear before
        _trace_id_ctx.set(None)
        _span_id_ctx.set(None)
        
        extract_trace_context(context_dict)
        
        # The context should be set correctly
        # We need to compare the full strings, not just the prefix
        self.assertEqual(_trace_id_ctx.get(), trace_id)
        self.assertEqual(_span_id_ctx.get(), span_id)
        
    def test_extract_trace_context_invalid(self):
        # Test with invalid format
        context_dict = {"traceparent": "invalid-format"}
        _trace_id_ctx.set(None)
        _span_id_ctx.set(None)
        
        # Should not raise exception and context should remain None
        try:
            extract_trace_context(context_dict)
        except Exception:
            self.fail("extract_trace_context raised an exception for invalid input")
            
        self.assertIsNone(_trace_id_ctx.get())
        self.assertIsNone(_span_id_ctx.get())

if __name__ == '__main__':
    unittest.main()