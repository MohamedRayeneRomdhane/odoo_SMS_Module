#!/usr/bin/env python3
"""
Final test script to verify SMS view refresh functionality
"""

print("=== Final SMS View Refresh Test ===")

# Test 1: Check if refresh methods exist
print("\n1. Checking if refresh methods exist...")
try:
    gateway = env['sms.tunisiesms'].search([], limit=1)
    if gateway:
        print(f"✓ Found SMS gateway: {gateway.name}")
        
        # Test refresh method
        if hasattr(gateway, '_ensure_all_users_have_access'):
            print("✓ _ensure_all_users_have_access method exists")
        else:
            print("✗ _ensure_all_users_have_access method missing")
            
        if hasattr(gateway, 'action_refresh_user_access'):
            print("✓ action_refresh_user_access method exists")
        else:
            print("✗ action_refresh_user_access method missing")
            
        # Test if refresh button is working
        result = gateway.action_refresh_user_access()
        if result and result.get('type') == 'ir.actions.client':
            print("✓ Refresh button works")
        else:
            print("✗ Refresh button failed")
            
    else:
        print("✗ No SMS gateway found")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Check cron job
print("\n2. Checking cron job...")
try:
    cron_job = env['ir.cron'].search([('name', '=', 'Refresh SMS Access for All Users')])
    if cron_job:
        print(f"✓ Found cron job: {cron_job.name}")
        print(f"  Active: {cron_job.active}")
        print(f"  Interval: {cron_job.interval_number} {cron_job.interval_type}")
        
        # Test cron execution
        result = env['sms.tunisiesms'].refresh_user_access()
        print(f"✓ Cron execution result: {result}")
    else:
        print("✗ Cron job not found")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Check view refresh functionality
print("\n3. Testing view refresh functionality...")
try:
    # Get all users
    all_users = env['res.users'].search([('active', '=', True)])
    print(f"Total active users: {len(all_users)}")
    
    # Check SMS history model
    history_model = env['sms.tunisiesms.history']
    if hasattr(history_model, '_trigger_access_refresh'):
        print("✓ History model has _trigger_access_refresh method")
    else:
        print("✗ History model missing _trigger_access_refresh method")
        
    # Check SMS queue model
    queue_model = env['sms.tunisiesms.queue']
    if hasattr(queue_model, '_trigger_access_refresh'):
        print("✓ Queue model has _trigger_access_refresh method")
    else:
        print("✗ Queue model missing _trigger_access_refresh method")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Test actual access refresh
print("\n4. Testing actual access refresh...")
try:
    # Check current user access
    current_user = env.user
    print(f"Current user: {current_user.name}")
    
    # Check access before refresh
    env.cr.execute('SELECT COUNT(*) FROM res_smsserver_group_rel WHERE uid = %s', (current_user.id,))
    before_count = env.cr.fetchone()[0]
    print(f"User access before refresh: {before_count > 0}")
    
    # Trigger refresh
    gateway = env['sms.tunisiesms'].search([], limit=1)
    if gateway:
        gateway._ensure_all_users_have_access()
        
        # Check access after refresh
        env.cr.execute('SELECT COUNT(*) FROM res_smsserver_group_rel WHERE uid = %s', (current_user.id,))
        after_count = env.cr.fetchone()[0]
        print(f"User access after refresh: {after_count > 0}")
        
        # Check total users with access
        env.cr.execute('SELECT COUNT(*) FROM res_smsserver_group_rel')
        total_access = env.cr.fetchone()[0]
        print(f"Total users with SMS access: {total_access}")
        
        if after_count > 0:
            print("✓ Access refresh working correctly")
        else:
            print("✗ Access refresh failed")
            
    else:
        print("✗ No gateway found for testing")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n=== Test Complete ===")
print("If all tests pass, the view refresh functionality should work.")
print("Users should now see SMS history and queue automatically.")
