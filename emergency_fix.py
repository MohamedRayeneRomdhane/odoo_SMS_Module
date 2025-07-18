#!/usr/bin/env python3
"""
Emergency fix for SMS history visibility
"""

def fix_sms_history_visibility():
    """Emergency fix to make SMS history visible to all users"""
    
    print("=== Emergency SMS History Fix ===")
    
    # Force grant access to all users
    try:
        # Get all active users
        all_users = env['res.users'].search([('active', '=', True)])
        print(f"Found {len(all_users)} active users")
        
        # Get SMS gateway
        gateway = env['sms.tunisiesms'].search([], limit=1)
        if not gateway:
            print("No SMS gateway found!")
            return False
            
        print(f"Using gateway: {gateway.name}")
        
        # Check current users with access
        current_users = gateway.users_id
        print(f"Current users with access: {len(current_users)}")
        
        # Force add all users
        gateway.write({
            'users_id': [(6, 0, all_users.ids)]
        })
        
        # Clear all caches
        env.invalidate_all()
        env.registry.clear_caches()
        
        # Commit changes
        env.cr.commit()
        
        print("Access granted to all users")
        
        # Check SMS history records
        try:
            # Bypass access check temporarily
            env.cr.execute("SELECT COUNT(*) FROM sms_tunisiesms_history")
            total_records = env.cr.fetchone()[0]
            print(f"Total SMS history records in database: {total_records}")
            
            if total_records > 0:
                env.cr.execute("""
                    SELECT id, name, sms, "to", date_create 
                    FROM sms_tunisiesms_history 
                    ORDER BY date_create DESC 
                    LIMIT 5
                """)
                records = env.cr.fetchall()
                print("\nRecent SMS records:")
                for record in records:
                    print(f"  ID: {record[0]}, Name: {record[1]}, To: {record[3]}")
            
            # Force refresh SMS history model
            env['sms.tunisiesms.history'].invalidate_cache()
            
        except Exception as e:
            print(f"Error checking SMS history: {e}")
        
        # Check user access in junction table
        env.cr.execute("SELECT COUNT(*) FROM res_smsserver_group_rel")
        access_count = env.cr.fetchone()[0]
        print(f"Users with SMS access after fix: {access_count}")
        
        return True
        
    except Exception as e:
        print(f"Error in emergency fix: {e}")
        return False

# Run the fix
if fix_sms_history_visibility():
    print("\n✓ Emergency fix completed successfully!")
    print("Please refresh your browser to see the SMS history.")
else:
    print("\n✗ Emergency fix failed!")
    
print("\n=== Fix Complete ===")
