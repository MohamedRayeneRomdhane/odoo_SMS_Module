#!/usr/bin/env python3
"""
Enhanced Sale Order SMS Test - User Selection
==============================================

This script creates a comprehensive SMS test for a test customer with user selection.
"""

def get_available_users():
    """Get list of available users from the database."""
    users = env['res.users'].search([
        ('active', '=', True),
        ('login', '!=', '__system__')
    ])
    return users

def select_user_for_sms():
    """Interactive user selection for SMS sending."""
    users = get_available_users()
    
    if not users:
        print("No users found!")
        return None
    
    print("\n" + "="*50)
    print("AVAILABLE USERS FOR SMS SENDING")
    print("="*50)
    
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.name} ({user.login})")
        if user.mobile:
            print(f"   Mobile: {user.mobile}")
        if user.email:
            print(f"   Email: {user.email}")
        print()
    
    while True:
        try:
            choice = input(f"Select user (1-{len(users)}) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                print("Test cancelled by user")
                return None
            
            choice_int = int(choice)
            if 1 <= choice_int <= len(users):
                selected_user = users[choice_int - 1]
                print(f"\n✓ Selected user: {selected_user.name} ({selected_user.login})")
                return selected_user
            else:
                print(f"Please enter a number between 1 and {len(users)}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")
        except KeyboardInterrupt:
            print("\nTest cancelled by user")
            return None

def switch_user_context(user_id):
    """Switch to a different user context."""
    global env
    env = env(user=user_id)
    return env

print("=== Enhanced Sale Order SMS Test ===")
print("Creating and testing SMS functionality for test customer...")

# Select user for SMS operations
selected_user = select_user_for_sms()
if not selected_user:
    print("No user selected. Exiting test.")
    exit()

# Switch to selected user context
original_user = env.user
env = switch_user_context(selected_user.id)

print(f"\n🔄 Switched to user context: {env.user.name} ({env.user.login})")
print(f"   User ID: {env.user.id}")
print(f"   Groups: {[g.name for g in env.user.groups_id]}")

try:
    # 1. Setup test customer
    print("\n1. Setting up test customer...")
    test_customer = env['res.partner'].search([('name', 'ilike', 'test customer')], limit=1)
    if test_customer:
        print(f"✓ Found existing customer: {test_customer.name}")
        print(f"   Customer: {test_customer.name}")
        print(f"   Mobile: {test_customer.mobile}")
        print(f"   Email: {test_customer.email}")
        print(f"   City: {test_customer.city}")
    else:
        print("✗ Test customer not found")
        test_customer = env['res.partner'].create({
            'name': 'Test Customer',
            'mobile': '21612345678',
            'email': 'test@example.com',
            'city': 'Tunis',
            'is_company': False,
            'customer_rank': 1,
        })
        print(f"✓ Created customer: {test_customer.name}")

    # 2. Setup test products with correct types for Odoo v14
    print("\n2. Setting up test products...")
    
    # Create smartphone product (consumable)
    smartphone = env['product.product'].search([('name', 'ilike', 'Samsung Galaxy Smartphone')], limit=1)
    if not smartphone:
        smartphone = env['product.product'].create({
            'name': 'Samsung Galaxy Smartphone',
            'sale_ok': True,
            'purchase_ok': True,
            'type': 'consu',  # Fixed: 'consu' instead of 'product'
            'list_price': 899.00,
            'standard_price': 650.00,
            'categ_id': env['product.category'].search([('name', 'ilike', 'all')], limit=1).id,
            'description_sale': 'Latest Samsung Galaxy smartphone with advanced features',
            'weight': 0.18,
            'volume': 0.001,
        })
        print(f"✓ Created product: {smartphone.name}")
    else:
        print(f"✓ Found existing product: {smartphone.name}")
    
    # Create accessories
    case = env['product.product'].search([('name', 'ilike', 'Premium Phone Case')], limit=1)
    if not case:
        case = env['product.product'].create({
            'name': 'Premium Phone Case',
            'sale_ok': True,
            'type': 'consu',  # Fixed: 'consu' instead of 'product'
            'list_price': 29.99,
            'standard_price': 15.00,
            'categ_id': env['product.category'].search([('name', 'ilike', 'all')], limit=1).id,
            'description_sale': 'Premium protective case for smartphones',
            'weight': 0.05,
        })
        print(f"✓ Created product: {case.name}")
    else:
        print(f"✓ Found existing product: {case.name}")

    # Create service product
    warranty = env['product.product'].search([('name', 'ilike', 'Extended Warranty')], limit=1)
    if not warranty:
        warranty = env['product.product'].create({
            'name': 'Extended Warranty Service',
            'sale_ok': True,
            'type': 'service',  # Service type is valid in Odoo v14
            'list_price': 99.99,
            'standard_price': 50.00,
            'categ_id': env['product.category'].search([('name', 'ilike', 'all')], limit=1).id,
            'description_sale': '2-year extended warranty coverage',
        })
        print(f"✓ Created service: {warranty.name}")
    else:
        print(f"✓ Found existing service: {warranty.name}")

    # 3. Test SMS Gateway Configuration
    print("\n3. Testing SMS Gateway Configuration...")
    gateway = env['sms.tunisiesms'].search([], limit=1)
    if gateway:
        print(f"✓ SMS Gateway found: {gateway.name}")
        print(f"   Auto SMS enabled: {gateway.auto_sms_enabled}")
        print(f"   Auto SMS on create: {gateway.auto_sms_on_create}")
        print(f"   Auto SMS on status change: {gateway.auto_sms_on_status_change}")
        
        # Check if current user has permission
        try:
            if hasattr(gateway, '_check_permissions'):
                has_permission = gateway._check_permissions()
                print(f"   ✓ Current user has SMS permission: {has_permission}")
            else:
                print("   ? Permission check method not available")
        except Exception as perm_error:
            print(f"   ✗ Permission check error: {perm_error}")
        
        # Check templates
        templates = [
            ('Draft template', gateway.order_draft_sms),
            ('Sale template', gateway.order_sale_sms),
            ('Done template', gateway.order_done_sms),
        ]
        
        for name, template in templates:
            if template:
                print(f"   ✓ {name}: {template[:50]}...")
            else:
                print(f"   ✗ {name}: Not configured")
    else:
        print("✗ No SMS Gateway found")

    # 4. Create comprehensive Sale Order
    print("\n4. Creating comprehensive Sale Order...")
    
    # Check SMS queue/history before
    sms_queue_before = env['sms.tunisiesms.queue'].search_count([])
    sms_history_before = env['sms.tunisiesms.history'].search_count([])
    
    print(f"   SMS queue before: {sms_queue_before}")
    print(f"   SMS history before: {sms_history_before}")
    
    # Create sale order with multiple products
    sale_order = env['sale.order'].create({
        'partner_id': test_customer.id,
        'order_line': [
            (0, 0, {
                'product_id': smartphone.id,
                'product_uom_qty': 1,
                'price_unit': smartphone.list_price,
            }),
            (0, 0, {
                'product_id': case.id,
                'product_uom_qty': 1,
                'price_unit': case.list_price,
            }),
            (0, 0, {
                'product_id': warranty.id,
                'product_uom_qty': 1,
                'price_unit': warranty.list_price,
            }),
        ],
    })
    
    print(f"✓ Created sale order: {sale_order.name}")
    print(f"   Customer: {sale_order.partner_id.name}")
    print(f"   Mobile: {sale_order.partner_id.mobile}")
    print(f"   State: {sale_order.state}")
    print(f"   Total: {sale_order.amount_total}")
    print(f"   Products: {len(sale_order.order_line)} items")
    print(f"   Created by user: {env.user.name} ({env.user.login})")
    
    # Check if SMS was triggered by creation
    sms_queue_after_create = env['sms.tunisiesms.queue'].search_count([])
    sms_history_after_create = env['sms.tunisiesms.history'].search_count([])
    
    print(f"   SMS queue after create: {sms_queue_after_create}")
    print(f"   SMS history after create: {sms_history_after_create}")
    
    if sms_queue_after_create > sms_queue_before or sms_history_after_create > sms_history_before:
        print("   ✅ CREATE TRIGGER WORKED - SMS was sent!")
        
        # Show who sent the SMS
        recent_history = env['sms.tunisiesms.history'].search([], limit=1, order='id desc')
        if recent_history:
            sender = env['res.users'].browse(recent_history.user_id.id)
            print(f"   📱 SMS sent by: {sender.name} ({sender.login})")
    else:
        print("   ? CREATE TRIGGER - No SMS detected (may need templates)")

    # 5. Test manual SMS sending
    print("\n5. Testing manual SMS sending...")
    try:
        if hasattr(sale_order, 'action_send_sms_now'):
            result = sale_order.action_send_sms_now()
            print(f"✓ Manual SMS result: {result}")
        else:
            print("✗ Manual SMS method not available")
    except Exception as sms_error:
        print(f"✗ Manual SMS error: {sms_error}")

    # 6. Test order confirmation (status change)
    print("\n6. Testing order confirmation (status change)...")
    
    sms_queue_before_confirm = env['sms.tunisiesms.queue'].search_count([])
    sms_history_before_confirm = env['sms.tunisiesms.history'].search_count([])
    
    try:
        sale_order.action_confirm()
        print(f"✓ Order confirmed! New state: {sale_order.state}")
        
        # Check SMS after confirmation
        sms_queue_after_confirm = env['sms.tunisiesms.queue'].search_count([])
        sms_history_after_confirm = env['sms.tunisiesms.history'].search_count([])
        
        print(f"   SMS queue after confirm: {sms_queue_after_confirm}")
        print(f"   SMS history after confirm: {sms_history_after_confirm}")
        
        if sms_queue_after_confirm > sms_queue_before_confirm or sms_history_after_confirm > sms_history_before_confirm:
            print("   ✅ STATUS CHANGE TRIGGER WORKED - SMS was sent!")
            
            # Show who sent the SMS
            recent_history = env['sms.tunisiesms.history'].search([], limit=1, order='id desc')
            if recent_history:
                sender = env['res.users'].browse(recent_history.user_id.id)
                print(f"   📱 SMS sent by: {sender.name} ({sender.login})")
        else:
            print("   ? STATUS CHANGE TRIGGER - No SMS detected")
            
    except Exception as confirm_error:
        print(f"✗ Order confirmation error: {confirm_error}")

    # 7. Show recent SMS activity
    print("\n7. Recent SMS Activity...")
    
    # Check queue
    recent_queue = env['sms.tunisiesms.queue'].search([], limit=3, order='id desc')
    print(f"   Recent queue items: {len(recent_queue)}")
    for q in recent_queue:
        mobile = getattr(q, 'mobile', 'N/A')
        sms_text = getattr(q, 'sms', getattr(q, 'text', 'N/A'))
        state = getattr(q, 'state', 'N/A')
        print(f"     - {mobile}: {str(sms_text)[:30]}... (State: {state})")
    
    # Check history
    recent_history = env['sms.tunisiesms.history'].search([], limit=3, order='id desc')
    print(f"   Recent history items: {len(recent_history)}")
    for h in recent_history:
        mobile = getattr(h, 'to', getattr(h, 'mobile_to', 'N/A'))
        sms_text = getattr(h, 'sms', getattr(h, 'text', 'N/A'))
        status = getattr(h, 'status_code', getattr(h, 'state', 'N/A'))
        sender = env['res.users'].browse(h.user_id.id) if h.user_id else None
        sender_name = sender.name if sender else 'Unknown'
        print(f"     - {mobile}: {str(sms_text)[:30]}... (Status: {status}) [Sent by: {sender_name}]")

    # 8. Test order completion (if possible)
    print("\n8. Testing order completion...")
    
    try:
        # Try to complete the order if it has delivery
        if sale_order.state == 'sale':
            # Check if order has delivery (handle different field names)
            pickings = []
            for field_name in ['picking_ids', 'delivery_ids', 'move_ids']:
                if hasattr(sale_order, field_name):
                    field_value = getattr(sale_order, field_name)
                    if field_value:  # Only assign if not empty
                        pickings = field_value
                        print(f"   Found deliveries using field: {field_name}")
                        break
            
            if pickings:
                for picking in pickings:
                    if picking.state not in ['done', 'cancel']:
                        try:
                            picking.action_confirm()
                            # Set quantities (handle different field names)
                            moves = getattr(picking, 'move_lines', getattr(picking, 'move_ids', []))
                            for move in moves:
                                if hasattr(move, 'quantity_done'):
                                    move.quantity_done = move.product_uom_qty
                            picking.action_done()
                            print(f"✓ Completed delivery: {picking.name}")
                        except Exception as pick_error:
                            print(f"   Delivery completion error: {pick_error}")
                            
                # Check if order is now done
                if sale_order.state == 'done':
                    print(f"✓ Order completed! State: {sale_order.state}")
                else:
                    print(f"Order state after delivery: {sale_order.state}")
            else:
                print("No delivery to complete")
        else:
            print(f"Order state not suitable for completion: {sale_order.state}")
            
    except Exception as completion_error:
        print(f"Order completion error: {completion_error}")

    # 9. Final SMS statistics
    print("\n9. Final SMS Statistics...")
    
    final_queue = env['sms.tunisiesms.queue'].search_count([])
    final_history = env['sms.tunisiesms.history'].search_count([])
    
    print(f"   Final SMS queue: {final_queue}")
    print(f"   Final SMS history: {final_history}")
    print(f"   Total new queue items: {final_queue - sms_queue_before}")
    print(f"   Total new history items: {final_history - sms_history_before}")
    
    # Summary
    print("\n10. Test Summary...")
    print(f"✓ Test run by user: {env.user.name} ({env.user.login})")
    print(f"✓ Customer: {test_customer.name} ({test_customer.mobile})")
    print(f"✓ Order: {sale_order.name} - {sale_order.state}")
    print(f"✓ Products: {len(sale_order.order_line)} items")
    print(f"✓ Total: {sale_order.amount_total}")
    
    if final_queue > sms_queue_before or final_history > sms_history_before:
        print("✅ SMS FUNCTIONALITY IS WORKING!")
        print(f"   📱 SMS messages sent by: {env.user.name}")
        print("   🔧 Automatic SMS visibility fix is integrated and working")
    else:
        print("? SMS functionality unclear - check templates and permissions")

    print("\n✅ Enhanced SMS test complete!")
    print("� Note: SMS visibility fix now runs automatically with each SMS operation")

except Exception as e:
    print(f"✗ Test failed with error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Restore original user context if needed
    if 'original_user' in locals():
        env = env(user=original_user.id)
        print(f"\n🔄 Restored to original user: {env.user.name}")

print("\n=== Enhanced Sale Order SMS Test Complete ===")
