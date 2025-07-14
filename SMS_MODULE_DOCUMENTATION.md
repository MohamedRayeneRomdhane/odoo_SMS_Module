# 📱 Odoo SMS Module - Complete Testing Documentation

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Testing Process](#detailed-testing-process)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Success Criteria](#success-criteria)
- [Appendix](#appendix)

---

## Overview

This documentation provides a comprehensive guide for testing the Odoo SMS Module that integrates with TUNISIESMS gateway. The module enables automatic SMS notifications for sale orders and manual SMS sending functionality.

### Key Features Tested
- **Permission Management**: SMS server permission validation and fixing
- **Order Integration**: Automatic SMS on sale order confirmation
- **Manual SMS**: Direct SMS sending capability
- **Queue Management**: SMS queue and history tracking
- **Gateway Integration**: TUNISIESMS API communication

---

## Prerequisites

### Environment Requirements
- **Docker Environment**: Odoo 14 running in Docker containers
- **Database**: PostgreSQL with test database named "test"
- **SMS Gateway**: TUNISIESMS account with valid credentials
- **Network**: Internet connectivity for SMS gateway API calls

### Container Setup
```bash
# Verify containers are running
docker ps

# Expected containers:
# sms-odoo-1    (Odoo application)
# sms-db-1      (PostgreSQL database)
```

### Required Files
- `fix_sms_permissions_corrected.py` - Permission fix script
- `basic_order_sms_test.py` - Enhanced SMS testing script

---

## Quick Start

### 1. Access Odoo Shell
```bash
docker exec -it sms-odoo-1 odoo shell -d test
```

### 2. Fix SMS Permissions
```python
exec(open('/tmp/fix_sms_permissions_corrected.py').read())
```

### 3. Run SMS Tests
```python
exec(open('/tmp/enhanced_rayen_sms_test.py').read())
```

### 4. Verify Success
- ✅ No permission errors
- ✅ SMS sending returns `Result: True`
- ✅ SMS queue shows new entries

---

## Detailed Testing Process

### Phase 1: Environment Preparation

#### Step 1.1: Container Verification
```bash
# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

**Expected Output:**
```
NAMES         STATUS        PORTS
sms-odoo-1    Up X minutes  0.0.0.0:8060->8069/tcp
sms-db-1      Up X minutes  5432/tcp
```

#### Step 1.2: File Deployment
```bash
# Copy permission fix script
docker cp "c:\path\to\fix_sms_permissions_corrected.py" sms-odoo-1:/tmp/

# Copy SMS test script  
docker cp "c:\path\to\basic_order_sms_test.py" sms-odoo-1:/tmp/enhanced_rayen_sms_test.py

# Verify files copied
docker exec sms-odoo-1 ls -la /tmp/*.py
```

### Phase 2: Permission Management

#### Step 2.1: Access Odoo Shell
```bash
docker exec -it sms-odoo-1 odoo shell -d test
```

**Expected Shell Prompt:**
```
Python 3.x.x console for odoo
>>> 
```

#### Step 2.2: Execute Permission Fix
```python
exec(open('/tmp/fix_sms_permissions_corrected.py').read())
```

**Critical Success Indicators:**
```
✓ Rolled back any failed transactions
✗ OdooBot NOT in SMS server permissions table
Existing permissions (sid, uid): [(1, 2)]
Will use existing sid: 1
✅ Added OdooBot to SMS server permissions
🎉 SUCCESS: OdooBot now has SMS server permissions!
Gateway permission check result: True
✅ SMS gateway permission check PASSED!
🎉 SMS SENDING SUCCESS!
Final permission table state: [(1, 2), (1, 1)]
```

**Permission Table Analysis:**
- `(1, 2)` = Mitchell Admin (sid=1, uid=2)
- `(1, 1)` = OdooBot (sid=1, uid=1)

#### Step 2.3: Validate Permission Fix
```python
# Test permission check directly
gateway = env['sms.tunisiesms'].search([], limit=1)
permission_result = gateway._check_permissions()
print(f"Permission check: {permission_result}")  # Should be True
```

### Phase 3: Comprehensive SMS Testing

#### Step 3.1: Execute Enhanced SMS Test
```python
exec(open('/tmp/enhanced_rayen_sms_test.py').read())
```

#### Step 3.2: Test Workflow Validation

**Customer Setup Verification:**
```
1. Setting up customer Rayen...
✓ Found existing customer: Rayen
   Customer: Rayen
   Mobile: 21621365818
   Email: rayen@example.com
   City: Tunis
```

**Product Creation Verification:**
```
2. Setting up test products...
✓ Created product: Samsung Galaxy Smartphone
✓ Created product: Premium Phone Case
```

**Order Processing Verification:**
```
3. Creating sale order for Rayen...
✓ Created new order: S00041

4. Order Details:
   Order Number: S00041
   Customer: Rayen
   Customer Mobile: 21621365818
   Order State: draft → sale
   Total Amount: 949.0 USD
   Order Lines: 2 items
```

**SMS Gateway Status:**
```
5. Checking SMS Gateway and Permissions...
✓ SMS Gateway found: TUNISIESMS
   Current user: OdooBot (ID: 1)
   Gateway info: {'url': 'https://api.l2t.io/tn/v0/api/api.aspx'}
```

**SMS Processing Results:**
```
8. Testing Manual SMS Processing...
✓ Order SMS processing method exists
INFO: Sending SMS via TUNISIESMS to 21621365818
✓ Order SMS processing completed

11. Manual SMS Test to Rayen...
INFO: Sending SMS via TUNISIESMS to 21621365818
✓ Manual SMS sent successfully to Rayen
   Result: True
```

### Phase 4: Detailed Verification

#### Step 4.1: SMS Queue Analysis
```python
# Check SMS queue status
queue = env['sms.tunisiesms.queue'].search([])
print(f"Total queue items: {len(queue)}")

# Analyze queue entries
for sms in queue:
    if hasattr(sms, 'mobile') and hasattr(sms, 'state'):
        print(f"Mobile: {sms.mobile}, State: {sms.state}")
```

**Expected Queue States:**
- `draft` - SMS queued for sending
- `sent` - SMS successfully delivered
- `error` - SMS failed (gateway issue, not permission)

#### Step 4.2: SMS History Tracking
```python
# Check SMS history
history = env['sms.tunisiesms.history'].search([])
print(f"Total history items: {len(history)}")

# Filter for Rayen's SMS
rayen_sms = [h for h in history if hasattr(h, 'mobile') and 
             str(getattr(h, 'mobile', '')) == '21621365818']
print(f"SMS for Rayen: {len(rayen_sms)}")
```

#### Step 4.3: Direct SMS Test
```python
# Perform direct SMS sending test
gateway = env['sms.tunisiesms'].search([], limit=1)
rayen = env['res.partner'].search([('name', 'ilike', 'rayen')], limit=1)

if gateway and rayen and rayen.mobile:
    sms_data = type('SMSData', (), {
        'gateway': gateway,
        'mobile_to': rayen.mobile,
        'text': 'Final verification SMS test',
        'validity': 60,
        'classes1': '1',
        'coding': '1',
        'nostop1': False,
    })()
    
    result = env['sms.tunisiesms'].send_msg(sms_data)
    print(f"Direct SMS Result: {result}")
```

---

## Troubleshooting Guide

### Permission Issues

#### Issue: "You do not have permission to use gateway"
**Cause:** User not in `res_smsserver_group_rel` table  
**Solution:**
```python
# Run permission fix script
exec(open('/tmp/fix_sms_permissions_corrected.py').read())

# Verify fix
gateway = env['sms.tunisiesms'].search([], limit=1)
print(gateway._check_permissions())  # Should return True
```

#### Issue: "column 'gid' does not exist"
**Cause:** Incorrect column names in SQL queries  
**Solution:** Use corrected script with proper column names (`sid`, `uid`)

#### Issue: "current transaction is aborted"
**Cause:** Previous SQL error corrupted transaction  
**Solution:**
```python
# Rollback transaction
env.cr.rollback()
# Re-run permission fix
```

### SMS Sending Issues

#### SMS State: "error"
**Possible Causes:**
1. **Gateway Credentials Invalid**
   - Check TUNISIESMS username/password
   - Verify account is active

2. **Insufficient Credits**
   - Check SMS gateway account balance
   - Top up credits if necessary

3. **Mobile Number Format**
   - Ensure number includes country code
   - Format: 21621365818 (Tunisia)

4. **API Endpoint Issues**
   - Verify gateway URL is accessible
   - Check for API maintenance

#### SMS State: "draft" (Stuck)
**Cause:** SMS processor not running  
**Solution:**
```python
# Manually trigger SMS processing
env['sale.order'].process_order_sms_notifications()
```

### Database Issues

#### Table Access Problems
```python
# Check if permission table exists
env.cr.execute("SELECT * FROM res_smsserver_group_rel LIMIT 1")
result = env.cr.fetchall()
print(f"Permission table data: {result}")
```

#### Environment Issues
```python
# Verify current user context
print(f"Current user: {env.user.name} (ID: {env.user.id})")
print(f"Database: {env.cr.dbname}")
```

---

## Success Criteria

### ✅ Permission Management Success
- [ ] `gateway._check_permissions()` returns `True`
- [ ] Permission table contains user entry: `(1, 1)` for OdooBot
- [ ] No "permission denied" errors in logs
- [ ] User can execute SMS operations without restrictions

### ✅ SMS Functionality Success
- [ ] Customer creation works (Rayen with mobile 21621365818)
- [ ] Product setup completes (Samsung Galaxy + Phone Case)
- [ ] Order creation and confirmation succeeds
- [ ] Order confirmation triggers automatic SMS
- [ ] Manual SMS sending returns `Result: True`
- [ ] SMS queue shows new entries after processing
- [ ] SMS history tracks sent messages

### ✅ Integration Success
- [ ] TUNISIESMS gateway responds positively
- [ ] API communication established (log shows gateway calls)
- [ ] SMS queue processing functions correctly
- [ ] Mobile number format accepted by gateway
- [ ] No authentication or authorization errors

### ✅ Data Consistency Success
- [ ] Database entries created correctly
- [ ] Queue and history synchronized
- [ ] Customer data persists across tests
- [ ] Order state transitions properly (draft → sale)

---

## Performance Benchmarks

### Expected Response Times
- **Permission Check**: < 100ms
- **SMS Queue Addition**: < 200ms
- **Gateway API Call**: < 3 seconds
- **Order Confirmation**: < 500ms

### Expected Success Rates
- **Permission Fix**: 100% success rate
- **SMS Sending**: >95% success rate (depends on gateway)
- **Queue Processing**: 100% success rate
- **Order Creation**: 100% success rate

---

## Appendix

### A. Database Schema Reference

#### Permission Table Structure
```sql
Table: res_smsserver_group_rel
Columns:
  - sid (integer): Server/Group ID
  - uid (integer): User ID

Example Data:
  (1, 2) -- Mitchell Admin
  (1, 1) -- OdooBot
```

#### SMS Queue Table
```sql
Table: sms.tunisiesms.queue
Key Fields:
  - mobile: Recipient phone number
  - msg: SMS message content
  - state: draft/sent/error
  - gateway_id: Reference to SMS gateway
```

### B. SMS Gateway Configuration

#### TUNISIESMS Settings
- **API URL**: `https://api.l2t.io/tn/v0/api/api.aspx`
- **Method**: HTTP POST
- **Authentication**: Username/Password
- **Mobile Format**: International format (21621365818)

### C. Test Data Reference

#### Customer: Rayen
- **Name**: Rayen
- **Mobile**: 21621365818
- **Email**: rayen@example.com
- **City**: Tunis
- **Country**: Tunisia (TN)

#### Test Products
1. **Samsung Galaxy Smartphone**
   - Price: €899.00
   - Type: Product

2. **Premium Phone Case**
   - Price: €25.00
   - Quantity: 2 units

#### Test Order
- **Total Amount**: €949.00 (899 + 25×2)
- **State Flow**: draft → sale
- **SMS Trigger**: Order confirmation

### D. Cleanup Commands

#### Remove Test Files
```bash
# Remove all Python test files from container
docker exec --user root sms-odoo-1 sh -c "rm -f /tmp/*.py"

# Verify cleanup
docker exec sms-odoo-1 ls -la /tmp/
```

#### Reset Test Environment
```python
# Delete test orders (optional)
test_orders = env['sale.order'].search([('partner_id.name', 'ilike', 'rayen')])
test_orders.unlink()

# Clear SMS queue (optional)
test_sms = env['sms.tunisiesms.queue'].search([('mobile', '=', '21621365818')])
test_sms.unlink()
```

---

## Support Information

### Documentation Version
- **Version**: 1.0
- **Last Updated**: July 14, 2025
- **Odoo Version**: 14.0
- **SMS Module**: TUNISIESMS Integration

---

*This documentation is maintained as part of the Odoo SMS Module project. Please ensure you're using the latest version of both the module and this documentation.*
