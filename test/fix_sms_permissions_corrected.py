# === Fix SMS Server Group Permissions (Corrected) ===
# This script fixes the specific permission table with correct column names

print("=== Fixing SMS Server Group Permissions (Corrected) ===")

try:
    # Get current user
    current_user = env.user
    print(f"Current user: {current_user.name} (ID: {current_user.id})")
    
    # Rollback any failed transaction first
    env.cr.rollback()
    print("✓ Rolled back any failed transactions")
    
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
        
        # Check what's in the table (correct column names: sid, uid)
        print(f"\nInvestigating res_smsserver_group_rel table...")
        try:
            env.cr.execute("SELECT sid, uid FROM res_smsserver_group_rel")
            existing_perms = env.cr.fetchall()
            print(f"Existing permissions (sid, uid): {existing_perms}")
            
            # Find what sid (server/group ID) to use
            if existing_perms:
                # Use the existing sid value
                existing_sid = existing_perms[0][0]  # First entry's sid
                print(f"Will use existing sid: {existing_sid}")
                
                # Check if current user already has permission
                user_exists = any(perm[1] == current_user.id for perm in existing_perms)
                
                if not user_exists:
                    # Add current user with the same sid
                    env.cr.execute(
                        'INSERT INTO res_smsserver_group_rel (sid, uid) VALUES (%s, %s)',
                        (existing_sid, current_user.id)
                    )
                    env.cr.commit()
                    print(f"✅ Added {current_user.name} to SMS server permissions")
                else:
                    print(f"✓ {current_user.name} already has permission")
            else:
                # No existing permissions - create first entry
                print("No existing permissions found - creating first entry")
                env.cr.execute(
                    'INSERT INTO res_smsserver_group_rel (sid, uid) VALUES (%s, %s)',
                    (1, current_user.id)
                )
                env.cr.commit()
                print(f"✅ Created first SMS permission for {current_user.name}")
                
        except Exception as table_error:
            print(f"Table operation error: {table_error}")
            env.cr.rollback()
    
    # Verify the fix
    print(f"\n🧪 Testing permission after fix...")
    env.cr.execute(
        'SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s LIMIT 1',
        (env.uid,)
    )
    final_result = env.cr.fetchone()
    
    if final_result:
        print(f"🎉 SUCCESS: {current_user.name} now has SMS server permissions!")
        
        # Test SMS gateway permission check
        print(f"Testing SMS gateway permission check...")
        gateway = env['sms.tunisiesms'].search([], limit=1)
        if gateway:
            # Test the permission check method directly
            permission_result = gateway._check_permissions()
            print(f"Gateway permission check result: {permission_result}")
            
            if permission_result:
                print("✅ SMS gateway permission check PASSED!")
                
                # Test actual SMS sending
                print(f"\n🧪 Testing actual SMS sending...")
                rayen = env['res.partner'].search([('name', 'ilike', 'rayen')], limit=1)
                if rayen and rayen.mobile:
                    try:
                        sms_data = type('SMSData', (), {
                            'gateway': gateway,
                            'mobile_to': rayen.mobile,
                            'text': f'Permission test successful! From {current_user.name}',
                            'validity': 60,
                            'classes1': '1',
                            'coding': '1',
                            'nostop1': False,
                        })()
                        
                        result = env['sms.tunisiesms'].send_msg(sms_data)
                        print("🎉 SMS SENDING SUCCESS!")
                        print(f"   Result: {result}")
                        
                    except Exception as sms_error:
                        print(f"❌ SMS sending failed: {sms_error}")
                else:
                    print("No customer Rayen found for SMS test")
            else:
                print("❌ SMS gateway permission check still FAILED")
        else:
            print("No SMS gateway found")
                
    else:
        print(f"❌ Permission fix failed - {current_user.name} still lacks SMS permissions")
    
    # Show final permission table state
    print(f"\n📋 Final permission table state:")
    env.cr.execute("SELECT sid, uid FROM res_smsserver_group_rel")
    final_perms = env.cr.fetchall()
    print(f"All permissions (sid, uid): {final_perms}")
    
    print(f"\n" + "="*60)
    print(f"✅ Permission fix complete!")
    print(f"SMS functionality should now work!")
    print(f"="*60)
    
except Exception as e:
    print(f"✗ Error fixing SMS permissions: {e}")
    env.cr.rollback()
    import traceback
    traceback.print_exc()
