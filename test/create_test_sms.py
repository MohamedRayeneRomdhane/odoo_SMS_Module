#!/usr/bin/env python3
"""
Create test SMS record to verify the system is working
"""

# Create a test SMS history record
try:
    history_obj = env['sms.tunisiesms.history']
    
    # Get the SMS gateway
    gateway = env['sms.tunisiesms'].search([], limit=1)
    if not gateway:
        print("No SMS gateway found!")
        exit()
    
    print(f"Using gateway: {gateway.name}")
    
    # Create test SMS record
    test_record = history_obj.create({
        'name': 'Test SMS Record',
        'gateway_id': gateway.id,
        'sms': 'This is a test SMS message to verify the system is working.',
        'to': '+216123456789',
        'message_id': 'test_123',
        'status_code': '200',
        'status_mobile': '+216123456789',
        'status_msg': 'Test message sent successfully',
        'date_create': fields.Datetime.now(),
        'user_id': env.uid
    })
    
    print(f"Created test SMS record with ID: {test_record.id}")
    
    # Ensure current user has access
    current_user = env.user
    print(f"Current user: {current_user.name}")
    
    # Check if user has access
    env.cr.execute(
        'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s',
        (env.uid,)
    )
    has_access = bool(env.cr.fetchone())
    print(f"User has SMS access: {has_access}")
    
    if not has_access:
        print("Granting SMS access to current user...")
        # Add user to SMS access
        env.cr.execute(
            'INSERT INTO res_smsserver_group_rel (uid, gid) VALUES (%s, %s)',
            (env.uid, gateway.id)
        )
        env.cr.commit()
        print("Access granted!")
    
    # Test search with the current user
    history_records = history_obj.search([])
    print(f"SMS history records found: {len(history_records)}")
    
    for record in history_records:
        print(f"  - {record.name} (ID: {record.id}) - To: {record.to}")
    
    # Force refresh caches
    env.invalidate_all()
    env.registry.clear_caches()
    env.cr.commit()
    
    print("\nTest completed successfully!")
    print("Please refresh your browser to see the SMS history.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
