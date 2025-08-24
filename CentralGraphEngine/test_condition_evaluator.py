#!/usr/bin/env python3
"""
Test script for ConditionEvaluator
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/root/projects/atom_agents')

from CentralGraphEngine.condition_evaluator import ConditionEvaluator
from interfaces import Condition

def test_condition_evaluator():
    """Test the ConditionEvaluator with various conditions."""
    evaluator = ConditionEvaluator()
    
    # Test 1: Simple boolean condition
    condition1 = Condition(evaluator='CEL', expression='True')
    result1 = evaluator.evaluate(condition1, {})
    print(f"Test 1 - Simple True condition: {result1} (expected: True)")
    assert result1 == True
    
    # Test 2: Simple boolean condition
    condition2 = Condition(evaluator='CEL', expression='False')
    result2 = evaluator.evaluate(condition2, {})
    print(f"Test 2 - Simple False condition: {result2} (expected: False)")
    assert result2 == False
    
    # Test 3: Condition with context variables
    condition3 = Condition(evaluator='CEL', expression='result == "success"')
    context3 = {'result': 'success'}
    result3 = evaluator.evaluate(condition3, context3)
    print(f"Test 3 - Context condition (success): {result3} (expected: True)")
    assert result3 == True
    
    # Test 4: Condition with context variables
    condition4 = Condition(evaluator='CEL', expression='result == "success"')
    context4 = {'result': 'failure'}
    result4 = evaluator.evaluate(condition4, context4)
    print(f"Test 4 - Context condition (failure): {result4} (expected: False)")
    assert result4 == False
    
    # Test 5: Numeric comparison
    condition5 = Condition(evaluator='CEL', expression='score > 80')
    context5 = {'score': 90}
    result5 = evaluator.evaluate(condition5, context5)
    print(f"Test 5 - Numeric comparison (90 > 80): {result5} (expected: True)")
    assert result5 == True
    
    # Test 6: Numeric comparison
    condition6 = Condition(evaluator='CEL', expression='score > 80')
    context6 = {'score': 70}
    result6 = evaluator.evaluate(condition6, context6)
    print(f"Test 6 - Numeric comparison (70 > 80): {result6} (expected: False)")
    assert result6 == False
    
    # Test 7: None condition (should default to True)
    result7 = evaluator.evaluate(None, {})
    print(f"Test 7 - None condition: {result7} (expected: True)")
    assert result7 == True
    
    # Test 8: Unsupported evaluator type (we'll create a mock condition object)
    class MockCondition:
        def __init__(self, evaluator, expression):
            self.evaluator = evaluator
            self.expression = expression
    
    condition8 = MockCondition(evaluator='UNKNOWN', expression='True')
    result8 = evaluator.evaluate(condition8, {})
    print(f"Test 8 - Unsupported evaluator: {result8} (expected: False)")
    assert result8 == False
    
    print("All tests passed!")

if __name__ == "__main__":
    test_condition_evaluator()