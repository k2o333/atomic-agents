#!/usr/bin/env python3
"""
Test script to verify database connection configuration
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PersistenceService.config import DatabaseConfig
from PersistenceService.database import DatabaseManager

def test_database_connection():
    """Test the database connection with current configuration"""
    print("Testing database connection...")
    
    try:
        # Load configuration
        config = DatabaseConfig()
        print(f"Database Configuration:")
        print(f"  Host: {config.host}")
        print(f"  Port: {config.port}")
        print(f"  Database: {config.database}")
        print(f"  User: {config.user}")
        print(f"  Connection String: {config.connection_string}")
        
        # Test connection
        db_manager = DatabaseManager(config)
        conn = db_manager.get_connection()
        print("✓ Database connection successful!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✓ PostgreSQL version: {version[0]}")
        
        # Close connection
        cursor.close()
        db_manager.put_connection(conn)
        db_manager.close_all_connections()
        print("✓ Database connection test completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"✗ Database connection test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)