# Central Graph Engine Tests

This directory contains the test suite for the Central Graph Engine (M1).

## Test Cases Implemented

1. Process Pending Task with FinalAnswer
2. Process Task with Agent Failure
3. Main Loop with No Pending Tasks
4. Main Loop with Multiple Pending Tasks
5. Error Handling in Main Loop

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

## Test Structure

- `test_engine.py` - Main test suite implementing all test cases
- `test_runner.sh` - Bash script to run tests with proper environment setup
- `test.md` - Original test plan and specifications

The tests use Python's unittest framework with mocking to isolate the Central Graph Engine components for testing.