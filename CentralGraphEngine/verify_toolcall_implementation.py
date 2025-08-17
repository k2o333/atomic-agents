#!/usr/bin/env python3
"""
Simple verification script for ToolCallRequest handling in Central Graph Engine
"""

import sys
import os

# Add project root to path
sys.path.insert(0, '/root/projects/atom_agents')

def verify_implementations():
    """Verify that the required implementations are in place"""
    print("Verifying ToolCallRequest implementation...")
    
    # Check if update_task_context method exists in task repository
    try:
        from PersistenceService.repository.task_repository import TaskRepository
        if hasattr(TaskRepository, 'update_task_context'):
            print("✅ TaskRepository.update_task_context method exists")
        else:
            print("❌ TaskRepository.update_task_context method missing")
    except Exception as e:
        print(f"❌ Error importing TaskRepository: {e}")
    
    # Check if update_task_context method exists in service
    try:
        from PersistenceService.service import PersistenceService
        if hasattr(PersistenceService, 'update_task_context'):
            print("✅ PersistenceService.update_task_context method exists")
        else:
            print("❌ PersistenceService.update_task_context method missing")
    except Exception as e:
        print(f"❌ Error importing PersistenceService: {e}")
    
    # Check if ToolCallRequest handling is in engine.py
    try:
        with open('/root/projects/atom_agents/CentralGraphEngine/engine.py', 'r') as f:
            content = f.read()
            if 'isinstance(intent, ToolCallRequest)' in content:
                print("✅ ToolCallRequest handling logic found in engine.py")
            else:
                print("❌ ToolCallRequest handling logic missing from engine.py")
    except Exception as e:
        print(f"❌ Error reading engine.py: {e}")
    
    # Check if correct import is used
    try:
        with open('/root/projects/atom_agents/CentralGraphEngine/engine.py', 'r') as f:
            content = f.read()
            if 'from toolservices.service import ToolService' in content:
                print("✅ Correct ToolService import found in engine.py")
            else:
                print("❌ Incorrect ToolService import in engine.py")
    except Exception as e:
        print(f"❌ Error reading engine.py: {e}")
    
    print("\nVerification complete!")

if __name__ == "__main__":
    verify_implementations()