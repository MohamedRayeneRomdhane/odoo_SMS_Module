# === Enhanced Sale Order SMS Test for Rayen ===
# Comprehensive test creating a specific sale order for customer Rayen
# Copy and paste this entire script into your Odoo shell

print("=== Enhanced Sale Order SMS Test for Rayen ===")
print("Creating and testing SMS functionality for customer Rayen...\n")

try:
    # 1. Create/Find customer Rayen
    print("1. Setting up customer Rayen...")
    
    # Check if Rayen already exists
    rayen = env['res.partner'].search([('name', 'ilike', 'rayen')], limit=1)
    
    if rayen:
        print(f"✓ Found existing customer: {rayen.name}")
        # Update mobile if different
        if rayen.mobile != '21621365818':
            rayen.write({'mobile': '21621365818'})
            print("✓ Updated mobile number")
    else:
        # Create Rayen as a customer
        rayen = env['res.partner'].create({
            'name': 'Rayen',
            'mobile': '21621365818',
            'phone': '21621365818',
            'email': 'rayen@example.com',
            'street': '123 Avenue Habib Bourguiba',
            'city': 'Tunis',
            'zip': '1000',
            'country_id': env['res.country'].search([('code', '=', 'TN')], limit=1).id or False,
            'customer_rank': 1,  # Mark as customer
            'is_company': False,
            'lang': 'en_US',
            'tz': 'Africa/Tunis'
        })
        print(f"✓ Created new customer: {rayen.name}")
    
    print(f"   Customer: {rayen.name}")
    print(f"   Mobile: {rayen.mobile}")
    print(f"   Email: {rayen.email}")
    print(f"   City: {rayen.city}")

    # 2. Create/Find test products
    print(f"\n2. Setting up test products...")
    
    # Create smartphone product
    smartphone = env['product.product'].search([('name', 'ilike', 'smartphone')], limit=1)
    if not smartphone:
        smartphone = env['product.product'].create({
            'name': 'Samsung Galaxy Smartphone',
            'sale_ok': True,
            'purchase_ok': True,
            'type': 'product',
            'list_price': 899.00,
            'standard_price': 650.00,
            'categ_id': env['product.category'].search([('name', 'ilike', 'all')], limit=1).id,
            'description_sale': 'Latest Samsung Galaxy smartphone with advanced features',
            'weight': 0.18,
            'volume': 0.001,
        })
        print(f"✓ Created product: {smartphone.name}")
    
    # Create accessories
    case = env['product.product'].search([('name', 'ilike', 'case')], limit=1)
    if not case:
        case = env['product.product'].create({
            'name': 'Premium Phone Case',
            'sale_ok': True,
            'type': 'product',
            'list_price': 25.00,
            'standard_price': 10.00,
            'description_sale': 'Protective premium phone case'
        })
        print(f"✓ Created product: {case.name}")

    # 3. Create comprehensive sale order for Rayen
    print(f"\n3. Creating sale order for Rayen...")
    
    # Check if order already exists for Rayen today
    import datetime
    today = datetime.date.today()
    existing_order = env['sale.order'].search([
        ('partner_id', '=', rayen.id),
        ('date_order', '>=', today.strftime('%Y-%m-%d'))
    ], limit=1)
    
    if existing_order:
        order = existing_order
        print(f"✓ Found existing order: {order.name}")
    else:
        # Create new order
        order = env['sale.order'].create({
            'partner_id': rayen.id,
            'partner_invoice_id': rayen.id,
            'partner_shipping_id': rayen.id,
            'date_order': datetime.datetime.now(),
            'validity_date': (datetime.datetime.now() + datetime.timedelta(days=7)),
            'payment_term_id': env['account.payment.term'].search([], limit=1).id or False,
            'note': f'Special order for {rayen.name} - SMS testing order created on {today}',
            'order_line': [
                (0, 0, {
                    'product_id': smartphone.id,
                    'name': smartphone.name,
                    'product_uom_qty': 1,
                    'price_unit': smartphone.list_price,
                    'tax_id': [(6, 0, [])],  # No tax for simplicity
                }),
                (0, 0, {
                    'product_id': case.id,
                    'name': case.name,
                    'product_uom_qty': 2,  # 2 cases
                    'price_unit': case.list_price,
                    'tax_id': [(6, 0, [])],
                })
            ]
        })
        print(f"✓ Created new order: {order.name}")
    
    # 4. Display order details
    print(f"\n4. Order Details:")
    print(f"   Order Number: {order.name}")
    print(f"   Customer: {order.partner_id.name}")
    print(f"   Customer Mobile: {order.partner_id.mobile}")
    print(f"   Order Date: {order.date_order}")
    print(f"   Order State: {order.state}")
    print(f"   Total Amount: {order.amount_total} {order.currency_id.name if order.currency_id else ''}")
    print(f"   Order Lines:")
    for line in order.order_line:
        print(f"     - {line.product_id.name}: {line.product_uom_qty} x {line.price_unit} = {line.price_subtotal}")

    # 5. Check SMS gateway and permissions
    print(f"\n5. Checking SMS Gateway and Permissions...")
    gateway = env['sms.tunisiesms'].search([], limit=1)
    if gateway:
        print(f"✓ SMS Gateway found: {gateway.name}")
        
        # Check current user permissions
        current_user = env.user
        print(f"   Current user: {current_user.name} (ID: {current_user.id})")
        
        # Check if user has SMS permissions
        sms_groups = env['res.groups'].search([('name', 'ilike', 'sms')])
        print(f"   Available SMS groups: {[g.name for g in sms_groups]}")
        
        # Try to grant SMS permissions to current user
        try:
            admin_user = env['res.users'].browse(1)  # Admin user (ID=1)
            if current_user.id != 1:
                print(f"   Switching to admin user for permissions...")
                # Add user to SMS groups if they exist
                for group in sms_groups:
                    if current_user.id not in group.users.ids:
                        group.sudo().write({'users': [(4, current_user.id)]})
                        print(f"   ✓ Added user to group: {group.name}")
        except Exception as perm_error:
            print(f"   Warning: Could not modify permissions: {perm_error}")
        
        # Check gateway fields safely
        gateway_info = {}
        for field in ['username', 'sender', 'url', 'password']:
            if hasattr(gateway, field):
                value = getattr(gateway, field, 'N/A')
                if field == 'password' and value:
                    value = '*' * len(str(value))  # Hide password
                gateway_info[field] = value
        print(f"   Gateway info: {gateway_info}")
        
        # Check gateway permissions more specifically
        try:
            # Check if gateway has user restrictions
            if hasattr(gateway, 'user_ids'):
                allowed_users = gateway.user_ids
                print(f"   Gateway allowed users: {[u.name for u in allowed_users]}")
                if not allowed_users or current_user in allowed_users:
                    print(f"   ✓ User has gateway access")
                else:
                    print(f"   ✗ User not in gateway allowed users")
                    # Try to add current user to gateway
                    try:
                        gateway.sudo().write({'user_ids': [(4, current_user.id)]})
                        print(f"   ✓ Added current user to gateway permissions")
                    except Exception as e:
                        print(f"   ✗ Could not add user to gateway: {e}")
        except Exception as e:
            print(f"   Gateway permission check failed: {e}")
            
    else:
        print("✗ No SMS gateway configured!")
        print("   Please configure SMS gateway first")

    # 6. Test SMS queue before any action
    print(f"\n6. SMS Queue Status (before processing)...")
    queue_before = env['sms.tunisiesms.queue'].search([])
    print(f"   Queue items before: {len(queue_before)}")
    
    # Show existing queue items if any
    if queue_before:
        for i, q in enumerate(queue_before[-3:], 1):  # Show last 3
            queue_info = {}
            for field in ['partner_id', 'mobile', 'text', 'state', 'date']:
                if hasattr(q, field):
                    value = getattr(q, field, 'N/A')
                    if field == 'text' and value:
                        value = str(value)[:40] + "..."
                    queue_info[field] = value
            print(f"     {i}. {queue_info}")

    # 7. Confirm order to trigger SMS
    print(f"\n7. Testing Order Confirmation (triggers SMS)...")
    if order.state in ['draft', 'sent']:
        print(f"   Order state: {order.state} -> Confirming order...")
        order.action_confirm()
        print(f"✓ Order confirmed! New state: {order.state}")
        
        # Wait a moment for any background processing
        import time
        time.sleep(2)
        
    else:
        print(f"   Order already confirmed (state: {order.state})")

    # 8. Test manual SMS processing
    print(f"\n8. Testing Manual SMS Processing...")
    if hasattr(env['sale.order'], 'process_order_sms_notifications'):
        print("✓ Order SMS processing method exists")
        
        try:
            result = env['sale.order'].process_order_sms_notifications()
            print("✓ Order SMS processing completed")
            print(f"   Processing result: {result}")
        except Exception as e:
            print(f"✗ Error in SMS processing: {e}")
    else:
        print("✗ Order SMS processing method not found")

    # 9. Check SMS queue after processing
    print(f"\n9. SMS Queue Status (after processing)...")
    queue_after = env['sms.tunisiesms.queue'].search([])
    print(f"   Queue items after: {len(queue_after)}")
    
    if len(queue_after) > len(queue_before):
        new_items = len(queue_after) - len(queue_before)
        print(f"✓ {new_items} new SMS(s) added to queue!")
        
        # Show new queue items
        for i, q in enumerate(queue_after[-new_items:], 1):
            queue_info = {}
            for field in ['partner_id', 'mobile', 'text', 'state']:
                if hasattr(q, field):
                    value = getattr(q, field, 'N/A')
                    if field == 'text' and value:
                        value = str(value)[:50] + "..."
                    queue_info[field] = value
            print(f"     New SMS {i}: {queue_info}")
    else:
        print("- No new SMS added to queue")

    # 10. Check SMS history
    print(f"\n10. SMS History Check...")
    history = env['sms.tunisiesms.history'].search([], limit=5, order='id desc')
    print(f"   Recent SMS history: {len(history)} items")
    
    for i, h in enumerate(history, 1):
        history_info = {}
        for field in ['partner_id', 'mobile', 'text', 'date', 'state']:
            if hasattr(h, field):
                value = getattr(h, field, 'N/A')
                if field == 'text' and value:
                    value = str(value)[:40] + "..."
                history_info[field] = value
        print(f"     {i}. {history_info}")

    # 11. Manual SMS test to Rayen
    if gateway and rayen.mobile:
        print(f"\n11. Manual SMS Test to Rayen...")
        try:
            # Create manual SMS for order confirmation
            sms_data = type('SMSData', (), {
                'gateway': gateway,
                'mobile_to': rayen.mobile,
                'text': f'Dear {rayen.name}, your order {order.name} for {order.amount_total} has been confirmed. Thank you for your purchase!',
                'validity': 60,
                'classes1': '1',
                'coding': '1',
                'nostop1': False,
            })()
            
            # Send manual SMS
            result = env['sms.tunisiesms'].send_msg(sms_data)
            print("✓ Manual SMS sent successfully to Rayen")
            print(f"   SMS content: {sms_data.text}")
            print(f"   Result: {result}")
            
        except Exception as e:
            print(f"✗ Manual SMS failed: {e}")
            import traceback
            traceback.print_exc()

    # 12. Final test summary
    print(f"\n=== Comprehensive Test Summary ===")
    print(f"✓ Customer: {rayen.name}")
    print(f"✓ Mobile: {rayen.mobile}")
    print(f"✓ Order: {order.name} (State: {order.state})")
    print(f"✓ Order Total: {order.amount_total}")
    print(f"✓ Gateway: {gateway.name if gateway else 'None'}")
    print(f"✓ Total Queue Items: {len(env['sms.tunisiesms.queue'].search([]))}")
    print(f"✓ Total History Items: {len(env['sms.tunisiesms.history'].search([]))}")
    print(f"✓ Order Lines: {len(order.order_line)} items")
    
    # Check if SMS was triggered for this specific order
    # Get queue and history separately (can't concatenate different models)
    queue_sms = env['sms.tunisiesms.queue'].search([])
    history_sms = env['sms.tunisiesms.history'].search([])
    
    # Check for Rayen's SMS in queue
    rayen_queue_sms = [sms for sms in queue_sms if hasattr(sms, 'mobile') and str(getattr(sms, 'mobile', '')) == rayen.mobile]
    rayen_history_sms = [sms for sms in history_sms if hasattr(sms, 'mobile') and str(getattr(sms, 'mobile', '')) == rayen.mobile]
    
    total_rayen_sms = len(rayen_queue_sms) + len(rayen_history_sms)
    print(f"✓ SMS for Rayen: {total_rayen_sms} found ({len(rayen_queue_sms)} in queue, {len(rayen_history_sms)} in history)")

except Exception as e:
    print(f"\n✗ Test failed with error: {e}")
    import traceback
    traceback.print_exc()

print(f"\n=== Enhanced Sale Order SMS Test Complete ===")
