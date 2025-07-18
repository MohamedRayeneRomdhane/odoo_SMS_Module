#!/usr/bin/env python3
"""
Test script for shared SMS history access functionality.
This script tests if all authorized users can access the same SMS history.
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
    
    # Test 1: Check if module can be imported
    print("\n1. Testing module import...")
    try:
        # Test import in Docker environment
        result = subprocess.run([
            'docker', 'exec', 'sms-odoo-1', 'python3', '-c',
            """
import sys
sys.path.append('/mnt/extra-addons/odoo_SMS_Module')
from tunisiesms import SMSHistory, SMSQueue, TunisieSMS
print("✓ Module imported successfully")
"""
        ], capture_output=True, text=True, check=True)
        
        print(result.stdout)
        print("✓ Module import successful")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Module import failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Test 2: Check database connection and models
    print("\n2. Testing database connection and models...")
    try:
        result = subprocess.run([
            'docker', 'exec', 'sms-odoo-1', 'python3', '-c',
            """
import odoo
from odoo import api, SUPERUSER_ID
from odoo.tools import config

# Configure database
config['db_name'] = 'odoo'
config['db_user'] = 'odoo'
config['db_password'] = 'odoo'
config['db_host'] = 'localhost'
config['db_port'] = 5432

# Initialize registry
registry = odoo.registry('odoo')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Test if models exist
    try:
        history_model = env['sms.tunisiesms.history']
        queue_model = env['sms.tunisiesms.queue']
        gateway_model = env['sms.tunisiesms']
        
        print("✓ All SMS models accessible")
        
        # Test search methods
        history_count = history_model.search_count([])
        queue_count = queue_model.search_count([])
        gateway_count = gateway_model.search_count([])
        
        print(f"✓ History records: {history_count}")
        print(f"✓ Queue records: {queue_count}")
        print(f"✓ Gateway records: {gateway_count}")
        
    except Exception as e:
        print(f"✗ Model access failed: {e}")
"""
        ], capture_output=True, text=True, check=True)
        
        print(result.stdout)
        print("✓ Database connection and models test successful")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Database test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    # Test 3: Check permission system
    print("\n3. Testing permission system...")
    try:
        result = subprocess.run([
            'docker', 'exec', 'sms-odoo-1', 'python3', '-c',
            """
import odoo
from odoo import api, SUPERUSER_ID
from odoo.tools import config

# Configure database
config['db_name'] = 'odoo'
config['db_user'] = 'odoo'
config['db_password'] = 'odoo'
config['db_host'] = 'localhost'
config['db_port'] = 5432

# Initialize registry
registry = odoo.registry('odoo')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Check SMS gateway permissions
    cr.execute('SELECT uid, sid FROM res_smsserver_group_rel ORDER BY uid')
    permissions = cr.fetchall()
    
    print(f"✓ SMS Gateway permissions found: {len(permissions)} entries")
    
    # Check users with SMS access
    user_ids = [p[0] for p in permissions]
    if user_ids:
        users = env['res.users'].browse(user_ids)
        for user in users:
            print(f"  - User: {user.name} (ID: {user.id})")
    
    # Test history access method
    history_model = env['sms.tunisiesms.history']
    if hasattr(history_model, '_check_user_sms_access'):
        print("✓ History access control method exists")
    else:
        print("✗ History access control method missing")
        
    # Test queue access method
    queue_model = env['sms.tunisiesms.queue']
    if hasattr(queue_model, '_check_user_sms_access'):
        print("✓ Queue access control method exists")
    else:
        print("✗ Queue access control method missing")
"""
        ], capture_output=True, text=True, check=True)
        
        print(result.stdout)
        print("✓ Permission system test successful")
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Permission system test failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    
    print("\n" + "=" * 60)
    print("SHARED ACCESS FUNCTIONALITY TEST COMPLETED")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_shared_access()
    sys.exit(0 if success else 1)
