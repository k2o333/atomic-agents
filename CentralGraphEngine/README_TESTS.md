# Central Graph Engine Tests

This directory contains test suites for the Central Graph Engine (M1).

## Test Suites

### 1. Isolated Logic Tests (`test_engine_logic.py`)
This test suite validates the core logic of the Central Graph Engine without importing the engine module directly. This approach avoids issues with service dependencies and database connections.

Tests included:
1. Process Pending Task Logic with FinalAnswer
2. Process Task Logic with Agent Failure
3. Main Loop Logic with No Pending Tasks
4. Main Loop Logic with Multiple Pending Tasks
5. Error Handling Logic in Main Loop
6. Evaluate Condition Placeholder
7. Process Directives Placeholder
8. Handle Completed Task Logic

### 2. Original Test Plan (`test.md`)
This document contains the original test plan with detailed specifications for each test case.

## Running the Tests

### Run Isolated Logic Tests:
```bash
cd /root/projects/atom_agents
/root/projects/atom_agents/myenv311/bin/python -m unittest CentralGraphEngine.test_engine_logic -v
```

### Run with coverage (if coverage is installed):
```bash
cd /root/projects/atom_agents
/root/projects/atom_agents/myenv311/bin/python -m coverage run -m unittest CentralGraphEngine.test_engine_logic -v
```

## Test Case Descriptions

### Test Case 1: Process Pending Task with FinalAnswer
Verifies that the engine can process a pending task assigned to an Agent and correctly handle a FinalAnswer response.

### Test Case 2: Process Task with Agent Failure
Verifies that the engine correctly handles a task when the Agent returns a failure.

### Test Case 3: Main Loop with No Pending Tasks
Verifies that the main loop correctly handles the case when there are no pending tasks.

### Test Case 4: Main Loop with Multiple Pending Tasks
Verifies that the main loop correctly processes multiple pending tasks in sequence.

### Test Case 5: Error Handling in Main Loop
Verifies that the main loop gracefully handles unexpected errors and continues running.

## Implementation Notes

The tests use Python's unittest framework with mocking to isolate the components for testing. The isolated logic tests avoid importing the actual engine module to prevent database connection issues and service dependencies.

Each test case simulates the core logic of the corresponding functionality in the Central Graph Engine, validating the expected behavior without requiring actual service implementations or database connections.