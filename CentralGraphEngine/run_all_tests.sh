#!/bin/bash
# run_all_tests.sh - Script to run all Central Graph Engine tests

echo "Running Central Graph Engine Tests"
echo "================================="

# Navigate to the project root
cd /root/projects/atom_agents

echo "Running Isolated Logic Tests..."
echo "-------------------------------"
/root/projects/atom_agents/myenv311/bin/python -m unittest CentralGraphEngine.test_engine_logic -v

echo ""
echo "All tests completed."