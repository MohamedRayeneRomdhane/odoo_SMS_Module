#!/usr/bin/env python3
"""
Test script to check SMS access and view refresh functionality
"""

print("=== SMS Access and View Refresh Test ===")

# Check current SMS gateway configuration
print("\n1. Checking SMS Gateway Configuration...")
try:
    gateways = env['sms.tunisiesms'].search([])
    print(f"Found {len(gateways)} SMS gateways")
    
    for gateway in gateways:
        print(f"Gateway: {gateway.name} (ID: {gateway.id})")
        print(f"  Users with access: {len(gateway.users_id)}")
        print(f"  User names: {[user.name for user in gateway.users_id]}")
        
except Exception as e:
    print(f"Error checking gateways: {e}")

# Check current user SMS access
print("\n2. Checking Current User SMS Access...")
try:
    current_user = env.user
    print(f"Current user: {current_user.name} (ID: {current_user.id})")
    
    # Check direct access via res_smsserver_group_rel
    env.cr.execute(
        'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
        (current_user.id,)
    )
    has_direct_access = bool(env.cr.fetchone())
    print(f"Has direct SMS access: {has_direct_access}")
    
    # Check SMS history visibility
    history_count = env['sms.tunisiesms.history'].search_count([])
    print(f"SMS history records visible: {history_count}")
    
    # Check SMS queue visibility
    queue_count = env['sms.tunisiesms.queue'].search_count([])
    print(f"SMS queue records visible: {queue_count}")
    
except Exception as e:
    print(f"Error checking user access: {e}")

# Check all active users and their SMS access
print("\n3. Checking All Active Users...")
try:
    all_users = env['res.users'].search([('active', '=', True)])
    print(f"Total active users: {len(all_users)}")
    
    users_with_access = []
    for user in all_users:
        env.cr.execute(
            'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
            (user.id,)
        )
        has_access = bool(env.cr.fetchone())
        if has_access:
            users_with_access.append(user.name)
    
    print(f"Users with SMS access: {len(users_with_access)}")
    print(f"Users with access: {users_with_access}")
    
except Exception as e:
    print(f"Error checking all users: {e}")

# Test automatic refresh functionality
print("\n4. Testing Automatic Refresh...")
try:
    gateway = env['sms.tunisiesms'].search([], limit=1)
    if gateway:
        print(f"Testing refresh on gateway: {gateway.name}")
        
        # Check if refresh is needed
        should_refresh = gateway._should_refresh_access()
        print(f"Should refresh access: {should_refresh}")
        
        # Manually trigger refresh
        print("Triggering manual refresh...")
        gateway._ensure_all_users_have_access()
        print("Manual refresh completed")
        
        # Check again after refresh
        print("Checking access after refresh...")
        users_with_access_after = []
        for user in all_users:
            env.cr.execute(
                'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
                (user.id,)
            )
            has_access = bool(env.cr.fetchone())
            if has_access:
                users_with_access_after.append(user.name)
        
        print(f"Users with access after refresh: {len(users_with_access_after)}")
        print(f"Users: {users_with_access_after}")
        
except Exception as e:
    print(f"Error testing refresh: {e}")

# Test cron job
print("\n5. Testing Cron Job...")
try:
    cron_job = env['ir.cron'].search([('name', '=', 'Refresh SMS Access for All Users')])
    if cron_job:
        print(f"Found cron job: {cron_job.name}")
        print(f"Active: {cron_job.active}")
        print(f"Interval: {cron_job.interval_number} {cron_job.interval_type}")
        print(f"Next call: {cron_job.nextcall}")
        
        # Test cron execution
        print("Testing cron execution...")
        result = env['sms.tunisiesms'].refresh_user_access()
        print(f"Cron execution result: {result}")
        
    else:
        print("Cron job not found!")
        
except Exception as e:
    print(f"Error testing cron: {e}")

print("\n=== Test Complete ===")
