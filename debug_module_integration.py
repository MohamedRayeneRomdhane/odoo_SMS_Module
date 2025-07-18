#!/usr/bin/env python3
"""
Module Integration Debug Script
==============================
This script checks why the automatic SMS visibility refresh isn't working
and diagnoses the module integration issues.
"""

def check_module_integration():
    """Check if the module integration is working properly."""
    
    print("=== MODULE INTEGRATION DEBUG ===")
    print("Checking why automatic SMS visibility refresh isn't working...")
    print()
    
    # 1. Check if gateway exists
    print("1. Checking SMS Gateway...")
    try:
        gateway = env['sms.tunisiesms'].search([], limit=1)
        if gateway:
            print(f"✅ Gateway found: {gateway.name}")
            print(f"   ID: {gateway.id}")
        else:
            print("❌ No SMS gateway found")
            return
    except Exception as e:
        print(f"❌ Error finding gateway: {e}")
        return
    
    # 2. Check if new methods exist
    print("\n2. Checking new methods...")
    
    # Check refresh_user_access method
    if hasattr(gateway, 'refresh_user_access'):
        print("✅ refresh_user_access method EXISTS")
        try:
            result = gateway.refresh_user_access()
            print(f"   ✅ Method executed successfully: {result}")
        except Exception as e:
            print(f"   ❌ Method execution failed: {e}")
    else:
        print("❌ refresh_user_access method NOT found")
        
    # Check _ensure_all_users_have_access method
    if hasattr(gateway, '_ensure_all_users_have_access'):
        print("✅ _ensure_all_users_have_access method EXISTS")
        try:
            gateway._ensure_all_users_have_access()
            print("   ✅ Method executed successfully")
        except Exception as e:
            print(f"   ❌ Method execution failed: {e}")
    else:
        print("❌ _ensure_all_users_have_access method NOT found")
    
    # Check _should_refresh_access method
    if hasattr(gateway, '_should_refresh_access'):
        print("✅ _should_refresh_access method EXISTS")
        try:
            should_refresh = gateway._should_refresh_access()
            print(f"   ✅ Should refresh: {should_refresh}")
        except Exception as e:
            print(f"   ❌ Method execution failed: {e}")
    else:
        print("❌ _should_refresh_access method NOT found")
    
    # 3. Check if create/write methods are overridden
    print("\n3. Checking method overrides...")
    
    # Get the class to check method resolution
    cls = type(gateway)
    print(f"   Class: {cls}")
    
    # Check create method
    if hasattr(cls, 'create'):
        create_method = getattr(cls, 'create')
        print(f"✅ create method exists: {create_method}")
        
        # Check if it's our custom create method
        if hasattr(create_method, '__code__'):
            code = create_method.__code__
            if '_ensure_all_users_have_access' in code.co_names:
                print("   ✅ Custom create method with auto-refresh")
            else:
                print("   ❌ Standard create method (no auto-refresh)")
        else:
            print("   ? Cannot inspect create method")
    else:
        print("❌ create method not found")
    
    # Check write method
    if hasattr(cls, 'write'):
        write_method = getattr(cls, 'write')
        print(f"✅ write method exists: {write_method}")
        
        # Check if it's our custom write method
        if hasattr(write_method, '__code__'):
            code = write_method.__code__
            if '_ensure_all_users_have_access' in code.co_names:
                print("   ✅ Custom write method with auto-refresh")
            else:
                print("   ❌ Standard write method (no auto-refresh)")
        else:
            print("   ? Cannot inspect write method")
    else:
        print("❌ write method not found")
    
    # 4. Check cron job
    print("\n4. Checking cron job...")
    try:
        cron_job = env['ir.cron'].search([('name', '=', 'Refresh SMS Access for All Users')])
        if cron_job:
            print(f"✅ Cron job found: {cron_job.name}")
            print(f"   Active: {cron_job.active}")
            print(f"   Interval: {cron_job.interval_number} {cron_job.interval_type}")
            print(f"   Model: {cron_job.model_id.model}")
            print(f"   Code: {cron_job.code}")
            
            # Test cron job execution
            try:
                print("   Testing cron job execution...")
                # Execute the cron job code
                if cron_job.code:
                    model = env[cron_job.model_id.model]
                    exec(cron_job.code, {'model': model, 'env': env})
                    print("   ✅ Cron job executed successfully")
                else:
                    print("   ❌ Cron job has no code")
            except Exception as e:
                print(f"   ❌ Cron job execution failed: {e}")
        else:
            print("❌ Cron job not found")
    except Exception as e:
        print(f"❌ Error checking cron job: {e}")
    
    # 5. Check ResUsers extension
    print("\n5. Checking ResUsers extension...")
    try:
        res_users_cls = env['res.users'].__class__
        
        # Check if create method is overridden
        if hasattr(res_users_cls, 'create'):
            create_method = getattr(res_users_cls, 'create')
            if hasattr(create_method, '__code__'):
                code = create_method.__code__
                if 'sms.tunisiesms' in code.co_names:
                    print("✅ ResUsers create method extended for SMS")
                else:
                    print("❌ ResUsers create method not extended for SMS")
            else:
                print("? Cannot inspect ResUsers create method")
        
        # Check if write method is overridden
        if hasattr(res_users_cls, 'write'):
            write_method = getattr(res_users_cls, 'write')
            if hasattr(write_method, '__code__'):
                code = write_method.__code__
                if 'sms.tunisiesms' in code.co_names:
                    print("✅ ResUsers write method extended for SMS")
                else:
                    print("❌ ResUsers write method not extended for SMS")
            else:
                print("? Cannot inspect ResUsers write method")
                
    except Exception as e:
        print(f"❌ Error checking ResUsers extension: {e}")
    
    # 6. Check current user permissions
    print("\n6. Checking current user permissions...")
    try:
        current_user = env.user
        print(f"   Current user: {current_user.name} ({current_user.login})")
        
        # Check if user has SMS access
        if current_user.id in gateway.users_id.ids:
            print("   ✅ Current user has SMS access")
        else:
            print("   ❌ Current user doesn't have SMS access")
            
        # Check SMS history visibility
        history_count = env['sms.tunisiesms.history'].search_count([])
        print(f"   SMS history entries visible: {history_count}")
        
        # Check SMS queue visibility
        queue_count = env['sms.tunisiesms.queue'].search_count([])
        print(f"   SMS queue entries visible: {queue_count}")
        
    except Exception as e:
        print(f"❌ Error checking user permissions: {e}")
    
    # 7. Test manual refresh
    print("\n7. Testing manual refresh...")
    try:
        users_before = len(gateway.users_id)
        print(f"   Users before refresh: {users_before}")
        
        # Try to run the visibility fix
        gateway._ensure_all_users_have_access()
        
        gateway.invalidate_cache()
        users_after = len(gateway.users_id)
        print(f"   Users after refresh: {users_after}")
        
        if users_after >= users_before:
            print("   ✅ Manual refresh working")
        else:
            print("   ❌ Manual refresh not working")
            
    except Exception as e:
        print(f"   ❌ Manual refresh failed: {e}")
    
    print("\n=== DIAGNOSIS COMPLETE ===")
    
    # Summary
    print("\n📋 SUMMARY:")
    has_methods = hasattr(gateway, 'refresh_user_access') and hasattr(gateway, '_ensure_all_users_have_access')
    has_cron = env['ir.cron'].search([('name', '=', 'Refresh SMS Access for All Users')])
    
    if has_methods and has_cron:
        print("✅ Module integration appears to be installed correctly")
        print("❓ The issue might be:")
        print("   - Cron job not running (check interval/timing)")
        print("   - Method overrides not working (check module update)")
        print("   - Permission issues (check user access)")
    else:
        print("❌ Module integration is incomplete:")
        if not has_methods:
            print("   - Missing automatic refresh methods")
        if not has_cron:
            print("   - Missing cron job")
        print("   - Module needs to be updated/reinstalled")
    
    print("\n🔧 RECOMMENDED ACTIONS:")
    print("1. Update the module: docker exec -it sms-odoo-1 odoo -d odoo -u odoo_SMS_Module --stop-after-init")
    print("2. Restart container: docker restart sms-odoo-1")
    print("3. Run manual fix: exec(open('/tmp/fix_visibility.py').read())")
    print("4. Check cron job logs in Odoo interface")

# Auto-run the function when script is executed
try:
    check_module_integration()
except Exception as e:
    print(f"❌ Debug script failed: {e}")
    import traceback
    traceback.print_exc()
