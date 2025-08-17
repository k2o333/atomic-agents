#!/bin/bash
# test_runner.sh - Script to run Central Graph Engine tests

echo "Running Central Graph Engine Tests"
echo "================================="

# Navigate to the project root
cd /root/projects/atom_agents

# Run the tests with verbose output
echo "Running tests with verbose output..."
python -m pytest CentralGraphEngine/test_engine.py -v

echo ""
echo "Test run completed."