#!/bin/bash

echo "=== SMS Module Testing Script ==="
echo "Run these commands in Odoo shell or create a test script"
echo ""

echo "1. Test SMS Queue Processing:"
echo "   env['sms.tunisiesms']._check_queue()"
echo ""

echo "2. Test Order SMS Processing:"
echo "   env['sale.order'].process_order_sms_notifications()"
echo ""

echo "3. Test Partner SMS Processing:"
echo "   env['res.partner'].process_partner_sms_notifications()"
echo ""

echo "4. Test DLR Status Updates:"
echo "   env['sms.tunisiesms'].get_dlr_status_updates()"
echo ""

echo "5. Check SMS Queue:"
echo "   queue = env['sms.tunisiesms.queue'].search([])"
echo "   print(f'Queue items: {len(queue)}')"
echo ""

echo "6. Check SMS History:"
echo "   history = env['sms.tunisiesms.history'].search([])"
echo "   print(f'History items: {len(history)}')"
echo ""

echo "7. Manual SMS Send Test:"
echo "   sms_data = type('SMSData', (), {"
echo "       'gateway': env['sms.tunisiesms'].search([], limit=1),"
echo "       'mobile_to': '+1234567890',"
echo "       'text': 'Test message',"
echo "       'validity': 60,"
echo "       'classes1': '1',"
echo "       'coding': '1',"
echo "       'nostop1': False,"
echo "   })()"
echo "   env['sms.tunisiesms'].send_msg(sms_data)"
