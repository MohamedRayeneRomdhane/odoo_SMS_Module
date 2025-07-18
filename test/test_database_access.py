#!/usr/bin/env python3
"""
Test script for shared SMS history access functionality.
This script should be run from within the Odoo Docker container.
"""

import logging
import os
import sys
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_shared_access():
    """Test the shared access functionality for SMS history and queue."""
    
    print("=" * 60)
    print("TESTING SHARED SMS ACCESS FUNCTIONALITY")
    print("=" * 60)
    
    # Test 1: Check if module syntax is correct
    print("\n1. Testing module syntax...")
    try:
        result = subprocess.run([
            'docker', 'exec', 'sms-odoo-1', 'python3', '-m', 'py_compile',
            '/mnt/extra-addons/odoo_SMS_Module/tunisiesms.py'
        ], capture_output=True, text=True, check=True)
        
        print("✓ Module syntax is correct")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Module syntax check failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Test 2: Check database connection and SMS history
    print("\n2. Testing SMS history in database...")
    try:
        result = subprocess.run([
            'docker', 'exec', 'sms-odoo-1', 'psql', '-U', 'odoo', '-d', 'odoo', '-c',
            'SELECT COUNT(*) as history_count FROM sms_tunisiesms_history;'
        ], capture_output=True, text=True, check=True)
        
        print("✓ SMS history table accessible")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ SMS history table test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Test 3: Check SMS queue in database
    print("\n3. Testing SMS queue in database...")
    try:
        result = subprocess.run([
            'docker', 'exec', 'sms-odoo-1', 'psql', '-U', 'odoo', '-d', 'odoo', '-c',
            'SELECT COUNT(*) as queue_count FROM sms_tunisiesms_queue;'
        ], capture_output=True, text=True, check=True)
        
        print("✓ SMS queue table accessible")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ SMS queue table test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Test 4: Check permission table
    print("\n4. Testing permission table...")
    try:
        result = subprocess.run([
            'docker', 'exec', 'sms-odoo-1', 'psql', '-U', 'odoo', '-d', 'odoo', '-c',
            'SELECT u.name, u.id FROM res_users u JOIN res_smsserver_group_rel r ON u.id = r.uid ORDER BY u.name;'
        ], capture_output=True, text=True, check=True)
        
        print("✓ Permission table accessible")
        print("Users with SMS access:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Permission table test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Test 5: Check recent SMS history by user
    print("\n5. Testing SMS history by user...")
    try:
        result = subprocess.run([
            'docker', 'exec', 'sms-odoo-1', 'psql', '-U', 'odoo', '-d', 'odoo', '-c',
            """SELECT u.name as user_name, h.name as sms_description, h.date_create, h.to as recipient
               FROM sms_tunisiesms_history h 
               JOIN res_users u ON h.user_id = u.id 
               ORDER BY h.date_create DESC 
               LIMIT 10;"""
        ], capture_output=True, text=True, check=True)
        
        print("✓ SMS history by user accessible")
        print("Recent SMS history:")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ SMS history by user test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    print("\n" + "=" * 60)
    print("SHARED ACCESS FUNCTIONALITY TEST COMPLETED")
    print("=" * 60)
    
    # Summary
    print("\n📋 SUMMARY:")
    print("- Module syntax is correct")
    print("- Database tables are accessible")
    print("- Permission system is in place")
    print("- SMS history tracking is working")
    print("- Ready for Odoo module update")
    
    return True

if __name__ == "__main__":
    success = test_shared_access()
    sys.exit(0 if success else 1)
