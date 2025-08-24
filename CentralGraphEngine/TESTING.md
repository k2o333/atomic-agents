# Central Graph Engine Tests (Ultimate Version)

This directory contains the test suite for the Central Graph Engine ultimate version with all advanced features.

## Test Cases Implemented

### M1 Core Tests
1. Process Pending Task with FinalAnswer
2. Process Task with Agent Failure
3. Main Loop with No Pending Tasks
4. Main Loop with Multiple Pending Tasks
5. Error Handling in Main Loop

### M2 Enhancement Tests
6. Process Pending Task with ToolCallRequest

### M3 Ultimate Version Tests
7. Process Pending Task with PlanBlueprint
8. Handle Completed Task with Edge Conditions
9. Condition Evaluation with Various Expressions
10. Data Flow Mapping
11. Redis BRPOP Integration

## Running the Tests

### Using the test runner script:
```bash
./test_runner.sh
```

### Directly with Python unittest:
```bash
cd /root/projects/atom_agents
python -m unittest CentralGraphEngine.test_engine -v
```

### With pytest (if installed):
```bash
cd /root/projects/atom_agents
python -m pytest CentralGraphEngine/test_engine.py -v
```

### Running Unit Tests for New Features:
```bash
# Run ConditionEvaluator unit tests
python -m CentralGraphEngine.test_condition_evaluator

# Run simple tests for data flow mapping and condition evaluation
python -m CentralGraphEngine.test_simple
```

## Test Structure

- `test_engine.py` - Main test suite implementing M1 and M2 test cases
- `test_condition_evaluator.py` - Unit tests for ConditionEvaluator
- `test_simple.py` - Simple tests for data flow mapping and condition evaluation
- `test_runner.sh` - Bash script to run tests with proper environment setup
- `test.md` - Comprehensive test plan and specifications with actual results

## Test Status

### ✅ Fully Tested and Verified
- ConditionEvaluator with comprehensive test coverage
- Data flow mapping functionality
- PlanBlueprint processing logic (unit tested)

### ⚠️ Implemented but Integration Testing Pending
- Edge condition routing (core logic implemented)
- Handle completed task workflow (structurally correct)
- Main loop with Redis integration (requires Redis server for full testing)
- Full end-to-end workflow integration

The tests use Python's unittest framework with mocking to isolate the Central Graph Engine components for testing. New tests have been added to verify the ultimate version features.