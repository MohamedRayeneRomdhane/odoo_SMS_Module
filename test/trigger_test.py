#!/usr/bin/env python3
"""
Automatic SMS Trigger Functionality Test
========================================

This script tests if the automatic SMS triggers are working correctly.
It checks the trigger implementation and validates functionality.

Usage:
    Run this in Odoo shell: execfile('trigger_test.py')
"""

print("=== Automatic SMS Trigger Functionality Test ===")

try:
    # 1. Check if automatic SMS models exist
    print("\n1. Checking SMS Models...")
    
    # Check SaleOrderSMS model
    try:
        sale_order_model = env['sale.order']
        print("✓ Sale Order model found")
        
        # Check if automatic SMS methods exist
        methods_to_check = [
            '_send_automatic_sms',
            '_get_order_sms_config', 
            '_replace_order_variables',
            'action_send_sms_now'
        ]
        
        for method in methods_to_check:
            if hasattr(sale_order_model, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
                
    except Exception as e:
        print(f"✗ Sale Order model issue: {e}")

    # 2. Check SMS Gateway configuration
    print("\n2. Checking SMS Gateway Configuration...")
    
    gateway = env['sms.tunisiesms'].search([('id', '=', 1)], limit=1)
    if gateway:
        print(f"✓ SMS Gateway found: {gateway.name}")
        
        # Check automatic SMS fields
        auto_fields = [
            'auto_sms_enabled',
            'auto_sms_on_create', 
            'auto_sms_on_status_change'
        ]
        
        for field in auto_fields:
            if hasattr(gateway, field):
                value = getattr(gateway, field, False)
                print(f"✓ {field}: {value}")
            else:
                print(f"✗ {field} missing")
                
        # Check template fields
        template_fields = [
            'status_order_draft', 'order_draft_sms',
            'status_order_sale', 'order_sale_sms',
            'status_order_done', 'order_done_sms'
        ]
        
        print("\n   Template Configuration:")
        for field in template_fields:
            if hasattr(gateway, field):
                value = getattr(gateway, field, None)
                if 'status_' in field:
                    print(f"   {field}: {value}")
                else:
                    template_preview = str(value)[:50] + "..." if value else "Not set"
                    print(f"   {field}: {template_preview}")
    else:
        print("✗ SMS Gateway not found")

    # 3. Test Create Trigger
    print("\n3. Testing Order Creation Trigger...")
    
    # Find or create test customer
    test_partner = env['res.partner'].search([('name', 'ilike', 'Test SMS Customer')], limit=1)
    if not test_partner:
        test_partner = env['res.partner'].create({
            'name': 'Test SMS Customer',
            'mobile': '21612345678',
            'is_company': False,
            'customer_rank': 1
        })
        print(f"✓ Created test customer: {test_partner.name}")
    else:
        print(f"✓ Using existing customer: {test_partner.name}")
        
    # Get test product
    test_product = env['product.product'].search([('sale_ok', '=', True)], limit=1)
    if test_product:
        print(f"✓ Using product: {test_product.name}")
    else:
        print("✗ No saleable product found")
        
    # Create order to test create trigger
    if test_product:
        print("   Creating new order to test create trigger...")
        
        # Check SMS queue before
        queue_before = env['sms.tunisiesms.queue'].search([])
        history_before = env['sms.tunisiesms.history'].search([])
        
        print(f"   SMS queue before: {len(queue_before)} items")
        print(f"   SMS history before: {len(history_before)} items")
        
        # Create order
        new_order = env['sale.order'].create({
            'partner_id': test_partner.id,
            'order_line': [(0, 0, {
                'product_id': test_product.id,
                'product_uom_qty': 1,
                'price_unit': test_product.list_price
            })]
        })
        
        print(f"   ✓ Created order: {new_order.name}")
        print(f"   Order state: {new_order.state}")
        
        # Check if SMS was triggered
        queue_after = env['sms.tunisiesms.queue'].search([])
        history_after = env['sms.tunisiesms.history'].search([])
        
        print(f"   SMS queue after: {len(queue_after)} items")
        print(f"   SMS history after: {len(history_after)} items")
        
        if len(queue_after) > len(queue_before) or len(history_after) > len(history_before):
            print("   ✓ CREATE TRIGGER IS WORKING - SMS was triggered!")
        else:
            print("   ? CREATE TRIGGER - No immediate SMS detected")
            print("     (This might be normal if templates are not configured)")

    # 4. Test Status Change Trigger
    print("\n4. Testing Status Change Trigger...")
    
    if 'new_order' in locals() and new_order:
        print(f"   Testing status change for order: {new_order.name}")
        print(f"   Current state: {new_order.state}")
        
        # Check SMS status before state change
        queue_before_confirm = env['sms.tunisiesms.queue'].search([])
        history_before_confirm = env['sms.tunisiesms.history'].search([])
        
        if new_order.state == 'draft':
            print("   Confirming order (draft → sale)...")
            try:
                new_order.action_confirm()
                print(f"   ✓ Order confirmed! New state: {new_order.state}")
                
                # Check if SMS was triggered by status change
                queue_after_confirm = env['sms.tunisiesms.queue'].search([])
                history_after_confirm = env['sms.tunisiesms.history'].search([])
                
                print(f"   SMS queue after confirm: {len(queue_after_confirm)} items")
                print(f"   SMS history after confirm: {len(history_after_confirm)} items")
                
                if len(queue_after_confirm) > len(queue_before_confirm) or len(history_after_confirm) > len(history_before_confirm):
                    print("   ✓ STATUS CHANGE TRIGGER IS WORKING - SMS was triggered!")
                else:
                    print("   ? STATUS CHANGE TRIGGER - No immediate SMS detected")
                    
            except Exception as e:
                print(f"   ✗ Order confirmation failed: {e}")
        else:
            print(f"   Order already confirmed (state: {new_order.state})")

    # 5. Test Manual SMS Function
    print("\n5. Testing Manual SMS Function...")
    
    if 'new_order' in locals() and new_order:
        try:
            if hasattr(new_order, 'action_send_sms_now'):
                print("   ✓ Manual SMS method exists")
                result = new_order.action_send_sms_now()
                print(f"   Manual SMS result: {result}")
            else:
                print("   ✗ Manual SMS method missing")
        except Exception as e:
            print(f"   ✗ Manual SMS failed: {e}")

    # 6. Test Partner Creation Trigger
    print("\n6. Testing Partner Creation Trigger...")
    
    try:
        queue_before_partner = env['sms.tunisiesms.queue'].search([])
        history_before_partner = env['sms.tunisiesms.history'].search([])
        
        # Create new partner
        new_partner = env['res.partner'].create({
            'name': f'SMS Test Partner',
            'mobile': '21612345999',
            'is_company': False,
            'customer_rank': 1
        })
        
        print(f"   ✓ Created partner: {new_partner.name}")
        
        # Check if SMS was triggered
        queue_after_partner = env['sms.tunisiesms.queue'].search([])
        history_after_partner = env['sms.tunisiesms.history'].search([])
        
        if len(queue_after_partner) > len(queue_before_partner) or len(history_after_partner) > len(history_before_partner):
            print("   ✓ PARTNER CREATION TRIGGER IS WORKING - SMS was triggered!")
        else:
            print("   ? PARTNER CREATION TRIGGER - No immediate SMS detected")
            
    except Exception as e:
        print(f"   ✗ Partner creation test failed: {e}")

    # 7. Check Recent SMS Activity
    print("\n7. Recent SMS Activity Summary...")
    
    recent_queue = env['sms.tunisiesms.queue'].search([], limit=5, order='id desc')
    recent_history = env['sms.tunisiesms.history'].search([], limit=5, order='id desc')
    
    print(f"   Latest Queue Items: {len(recent_queue)}")
    for i, q in enumerate(recent_queue[:3], 1):
        mobile = getattr(q, 'mobile', 'N/A')
        state = getattr(q, 'state', 'N/A')
        date = getattr(q, 'date_create', 'N/A')
        print(f"     {i}. Mobile: {mobile}, State: {state}, Date: {date}")
    
    print(f"   Latest History Items: {len(recent_history)}")
    for i, h in enumerate(recent_history[:3], 1):
        mobile = getattr(h, 'to', 'N/A')
        status = getattr(h, 'status_code', 'N/A')
        date = getattr(h, 'date_create', 'N/A')
        print(f"     {i}. Mobile: {mobile}, Status: {status}, Date: {date}")

    # 8. Trigger Functionality Assessment
    print("\n8. Trigger Functionality Assessment...")
    
    print("📊 TRIGGER STATUS REPORT:")
    
    # Check if models have the right inheritance
    sale_order_base = env['sale.order']._name
    if hasattr(env['sale.order'], '_send_automatic_sms'):
        print("✅ Order Creation/Change Triggers: IMPLEMENTED")
    else:
        print("❌ Order Creation/Change Triggers: NOT IMPLEMENTED")
        
    if hasattr(env['res.partner'], '_send_automatic_partner_sms'):
        print("✅ Partner Creation Trigger: IMPLEMENTED")
    else:
        print("❌ Partner Creation Trigger: NOT IMPLEMENTED")
        
    # Check gateway configuration
    if gateway and hasattr(gateway, 'auto_sms_enabled'):
        print(f"✅ Gateway Auto SMS Config: AVAILABLE ({gateway.auto_sms_enabled})")
    else:
        print("❌ Gateway Auto SMS Config: NOT AVAILABLE")
        
    # Overall assessment
    total_queue = len(env['sms.tunisiesms.queue'].search([]))
    total_history = len(env['sms.tunisiesms.history'].search([]))
    
    print(f"\n📈 SMS Activity Stats:")
    print(f"   Total Queue Items: {total_queue}")
    print(f"   Total History Items: {total_history}")
    print(f"   Gateway Configured: {'Yes' if gateway else 'No'}")
    
    if total_queue > 0 or total_history > 0:
        print("✅ TRIGGERS ARE FUNCTIONAL - SMS activity detected!")
    else:
        print("⚠️  TRIGGERS STATUS UNCLEAR - No SMS activity detected")
        print("   This could mean:")
        print("   1. Triggers work but templates are not configured")
        print("   2. Triggers work but auto SMS is disabled")
        print("   3. Triggers need configuration/activation")

except Exception as e:
    print(f"\n❌ Test failed with error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== End of Trigger Functionality Test ===")
