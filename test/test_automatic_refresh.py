#!/usr/bin/env python3
"""
Test script to verify automatic SMS access refresh functionality.
Tests both manual refresh and automatic user creation scenarios.

Run this script in Odoo shell:
docker exec -it sms-odoo-1 /opt/odoo/odoo-bin shell -d odoo --no-http -c /etc/odoo/odoo.conf
then: exec(open('/mnt/extra-addons/odoo_SMS_Module/test_automatic_refresh.py').read())
"""

import sys
import os
import time

def test_automatic_refresh():
    """Test the automatic SMS access refresh functionality."""
    
    print("=== Testing Automatic SMS Access Refresh ===\n")
    
    # 1. Test manual refresh
    print("1. Testing manual refresh...")
    try:
        gateways = env['sms.tunisiesms'].search([])
        print(f"Found {len(gateways)} SMS gateways")
        
        if gateways:
            gateway = gateways[0]
            print(f"Gateway: {gateway.name}")
            
            # Check current users
            current_users = gateway.users_id
            print(f"Current users with access: {len(current_users)}")
            
            # Get all users
            all_users = env['res.users'].search([('active', '=', True)])
            print(f"Total active users: {len(all_users)}")
            
            # Test manual refresh
            gateway.refresh_user_access()
            
            # Check after refresh
            gateway.invalidate_cache()
            updated_users = gateway.users_id
            print(f"Users after refresh: {len(updated_users)}")
            
            if len(updated_users) == len(all_users):
                print("✅ Manual refresh works correctly!")
            else:
                print("❌ Manual refresh failed")
        else:
            print("❌ No SMS gateways found")
            
    except Exception as e:
        print(f"❌ Error in manual refresh test: {e}")
    
    print("\n" + "="*50)
    
    # 2. Test automatic refresh method
    print("2. Testing automatic refresh method...")
    try:
        gateways = env['sms.tunisiesms'].search([])
        if gateways:
            gateway = gateways[0]
            
            # Test the _ensure_all_users_have_access method
            print("Testing _ensure_all_users_have_access...")
            gateway._ensure_all_users_have_access()
            
            # Verify all users have access
            all_users = env['res.users'].search([('active', '=', True)])
            gateway_users = gateway.users_id
            
            print(f"All users: {len(all_users)}")
            print(f"Gateway users: {len(gateway_users)}")
            
            if len(all_users) == len(gateway_users):
                print("✅ Automatic refresh method works correctly!")
            else:
                print("❌ Automatic refresh method failed")
                missing_users = set(all_users.ids) - set(gateway_users.ids)
                print(f"Missing users: {missing_users}")
                
    except Exception as e:
        print(f"❌ Error in automatic refresh test: {e}")
    
    print("\n" + "="*50)
    
    # 3. Test user creation scenario (simulation)
    print("3. Testing user creation scenario...")
    try:
        # Create a test user
        test_user_vals = {
            'name': 'Test SMS User',
            'login': f'test_sms_user_{int(time.time())}',
            'email': f'test_sms_user_{int(time.time())}@example.com',
            'active': True,
        }
        
        print("Creating test user...")
        test_user = env['res.users'].create(test_user_vals)
        print(f"Created test user: {test_user.name}")
        
        # Check if user automatically got SMS access
        gateways = env['sms.tunisiesms'].search([])
        if gateways:
            gateway = gateways[0]
            gateway.invalidate_cache()
            
            if test_user.id in gateway.users_id.ids:
                print("✅ New user automatically got SMS access!")
            else:
                print("❌ New user didn't get SMS access automatically")
                
        # Clean up test user
        test_user.unlink()
        print("Test user cleaned up")
        
    except Exception as e:
        print(f"❌ Error in user creation test: {e}")
    
    print("\n" + "="*50)
    
    # 4. Test cron job existence
    print("4. Testing cron job setup...")
    try:
        cron_job = env['ir.cron'].search([('name', '=', 'Refresh SMS Access for All Users')])
        if cron_job:
            print(f"✅ Cron job found: {cron_job.name}")
            print(f"   Interval: {cron_job.interval_number} {cron_job.interval_type}")
            print(f"   Active: {cron_job.active}")
            print(f"   Model: {cron_job.model_id.model}")
        else:
            print("❌ Cron job not found")
            
    except Exception as e:
        print(f"❌ Error checking cron job: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    try:
        import time
        test_automatic_refresh()
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)
