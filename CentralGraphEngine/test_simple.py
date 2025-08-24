#!/usr/bin/env python3
"""
Simple test for Central Graph Engine functions
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, '/root/projects/atom_agents')

from CentralGraphEngine.engine import apply_data_flow
from CentralGraphEngine.condition_evaluator import ConditionEvaluator
from interfaces import DataFlow, Condition

def test_apply_data_flow():
    """Test apply_data_flow function."""
    print("Testing apply_data_flow...")
    
    # Test with valid data flow
    data_flow = DataFlow(mappings={
        "target_field": "source_field",
        "another_field": "another_source"
    })
    
    source_result = {
        "source_field": "test_value",
        "another_source": 42,
        "extra_field": "extra_value"
    }
    
    result = apply_data_flow(data_flow, source_result)
    
    expected = {
        "target_field": "test_value",
        "another_field": 42
    }
    
    assert result == expected, f"Expected {expected}, got {result}"
    
    # Test with empty data flow
    empty_result = apply_data_flow(None, source_result)
    assert empty_result == {}, f"Expected empty dict, got {empty_result}"
    
    print("apply_data_flow test passed!")

def test_condition_evaluator():
    """Test ConditionEvaluator directly."""
    print("Testing ConditionEvaluator...")
    
    evaluator = ConditionEvaluator()
    
    # Test simple condition
    condition = Condition(evaluator='CEL', expression='True')
    result = evaluator.evaluate(condition, {})
    assert result == True, f"Expected True, got {result}"
    
    # Test context-based condition
    condition2 = Condition(evaluator='CEL', expression='score > 80')
    context = {'score': 90}
    result2 = evaluator.evaluate(condition2, context)
    assert result2 == True, f"Expected True, got {result2}"
    
    print("ConditionEvaluator test passed!")

def run_all_tests():
    """Run all tests."""
    print("Running Central Graph Engine Simple Tests...")
    print("=" * 50)
    
    try:
        test_apply_data_flow()
        test_condition_evaluator()
        
        print("=" * 50)
        print("All simple tests passed!")
        return True
    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)