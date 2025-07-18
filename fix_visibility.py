#!/usr/bin/env python3
"""
Fix SMS interface visibility for all users
"""

def fix_sms_interface_visibility():
    """Fix SMS interface visibility by adding all users to gateway permissions."""
    
    print("🔧 FIXING SMS INTERFACE VISIBILITY")
    print("=" * 50)
    
    # Get SMS gateway
    gateway = env['sms.tunisiesms'].search([('name', '=', 'TUNISIESMS')], limit=1)
    if not gateway:
        print("❌ SMS Gateway not found!")
        return False
    
    print(f"📱 SMS Gateway: {gateway.name}")
    
    # Get all active users
    all_users = env['res.users'].search([('active', '=', True)])
    print(f"👥 Total active users: {len(all_users)}")
    
    # Check current users with access
    current_users = gateway.users_id
    print(f"📊 Current users with SMS access: {len(current_users)}")
    for user in current_users:
        print(f"   - {user.name} ({user.login})")
    
    # Add all users to gateway permissions
    print("\n🔄 Adding all users to SMS gateway permissions...")
    gateway.write({
        'users_id': [(6, 0, all_users.ids)]
    })
    
    # Verify the update
    updated_users = gateway.users_id
    print(f"✅ Updated users with SMS access: {len(updated_users)}")
    for user in updated_users:
        print(f"   - {user.name} ({user.login})")
    
    # Test SMS history visibility for each user
    print("\n🧪 Testing SMS history visibility for each user...")
    for user in all_users:
        try:
            # Test as this user
            history_count = env['sms.tunisiesms.history'].sudo(user).search_count([])
            print(f"   {user.name}: {history_count} SMS history entries visible")
        except Exception as e:
            print(f"   {user.name}: Error - {e}")
    
    # Commit changes
    env.cr.commit()
    print("\n💾 Changes committed to database")
    
    return True

# Run the fix
if 'env' in globals():
    fix_sms_interface_visibility()
else:
    print("❌ This script must be run in Odoo shell environment")