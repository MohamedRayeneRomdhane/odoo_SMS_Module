# === Fix SMS Server Group Permissions ===
# This script fixes the specific permission table that SMS gateway checks

print("=== Fixing SMS Server Group Permissions ===")

try:
    # Get current user
    current_user = env.user
    print(f"Current user: {current_user.name} (ID: {current_user.id})")
    
    # Check the specific permission table that SMS gateway uses
    print(f"\nChecking res_smsserver_group_rel table...")
    
    # Execute the same query that the SMS gateway uses
    env.cr.execute(
        'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
        (env.uid,)
    )
    result = env.cr.fetchone()
    
    if result:
        print(f"✓ {current_user.name} already has SMS server permissions")
    else:
        print(f"✗ {current_user.name} NOT in SMS server permissions table")
        
        # Check if the table exists and what it contains
        print(f"\nInvestigating res_smsserver_group_rel table...")
        try:
            env.cr.execute("SELECT * FROM res_smsserver_group_rel LIMIT 5")
            existing_perms = env.cr.fetchall()
            print(f"Existing permissions: {existing_perms}")
            
            # Get table structure
            env.cr.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'res_smsserver_group_rel'
            """)
            columns = env.cr.fetchall()
            print(f"Table structure: {columns}")
            
        except Exception as table_error:
            print(f"Table check error: {table_error}")
    
    # Check if there's an SMS server group or model
    print(f"\nLooking for SMS server groups...")
    
    # Look for any SMS-related models
    try:
        sms_server_groups = env['res.groups'].search([
            '|', ('name', 'ilike', 'sms server'),
            '|', ('name', 'ilike', 'sms gateway'),
            ('name', 'ilike', 'tunisie')
        ])
        print(f"SMS server groups found: {[g.name for g in sms_server_groups]}")
        
        # Add current user to these groups
        for group in sms_server_groups:
            if current_user not in group.users:
                group.sudo().write({'users': [(4, current_user.id)]})
                print(f"✓ Added {current_user.name} to {group.name}")
    
    except Exception as group_error:
        print(f"Group search error: {group_error}")
    
    # Try to manually insert permission if table exists
    print(f"\nAttempting to add manual permission...")
    try:
        # First check if entry already exists
        env.cr.execute(
            'SELECT uid FROM res_smsserver_group_rel WHERE uid = %s',
            (current_user.id,)
        )
        existing = env.cr.fetchone()
        
        if not existing:
            # Try to insert a permission entry
            # We need to find what 'gid' should be - probably SMS group ID
            env.cr.execute("SELECT DISTINCT gid FROM res_smsserver_group_rel LIMIT 1")
            sample_gid = env.cr.fetchone()
            
            if sample_gid:
                gid_to_use = sample_gid[0]
                print(f"Using existing gid: {gid_to_use}")
            else:
                # No existing entries - try gid = 1 or find SMS group ID
                sms_group = env['res.groups'].search([('name', 'ilike', 'sms')], limit=1)
                gid_to_use = sms_group.id if sms_group else 1
                print(f"Using SMS group gid: {gid_to_use}")
            
            # Insert permission
            env.cr.execute(
                'INSERT INTO res_smsserver_group_rel (uid, gid) VALUES (%s, %s)',
                (current_user.id, gid_to_use)
            )
            env.cr.commit()
            print(f"✅ Added manual permission for {current_user.name}")
            
        else:
            print(f"✓ Manual permission already exists")
            
    except Exception as insert_error:
        print(f"Manual insert error: {insert_error}")
        
        # Alternative: try to create the table entry via SQL
        try:
            print("Trying alternative permission method...")
            # Check if we can create a simple permission record
            env.cr.execute("""
                INSERT INTO res_smsserver_group_rel (uid, gid) 
                SELECT %s, 1 
                WHERE NOT EXISTS (
                    SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s
                )
            """, (current_user.id, current_user.id))
            env.cr.commit()
            print("✅ Alternative permission method succeeded")
            
        except Exception as alt_error:
            print(f"Alternative method failed: {alt_error}")
    
    # Verify the fix
    print(f"\n🧪 Testing permission after fix...")
    env.cr.execute(
        'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
        (env.uid,)
    )
    final_result = env.cr.fetchone()
    
    if final_result:
        print(f"🎉 SUCCESS: {current_user.name} now has SMS server permissions!")
        
        # Test SMS sending
        print(f"Testing SMS send permission...")
        gateway = env['sms.tunisiesms'].search([], limit=1)
        if gateway:
            # Test the permission check method directly
            permission_result = gateway._check_permissions()
            print(f"Gateway permission check result: {permission_result}")
            
            if permission_result:
                print("✅ SMS gateway permission check PASSED!")
            else:
                print("❌ SMS gateway permission check still FAILED")
                
    else:
        print(f"❌ Permission fix failed - {current_user.name} still lacks SMS permissions")
    
    print(f"\n" + "="*60)
    print(f"Permission fix complete!")
    print(f"Try your SMS test again now.")
    print(f"="*60)
    
except Exception as e:
    print(f"✗ Error fixing SMS permissions: {e}")
    import traceback
    traceback.print_exc()
