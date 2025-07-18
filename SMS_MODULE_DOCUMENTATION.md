# 📱 Odoo SMS Module - Complete Documentation

## Table of Contents
- [Overview](#overview)
- [Module Architecture](#module-architecture)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Features](#features)
- [Testing Framework](#testing-framework)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)
- [Appendix](#appendix)

---

## Overview

This documentation provides a comprehensive guide for the Odoo SMS Module that integrates with TUNISIESMS gateway. The module enables automatic SMS notifications for sale orders, manual SMS sending, and comprehensive SMS management with built-in visibility fixes and robust permission management.

### Key Features
- **Automatic SMS Notifications**: Send SMS automatically on sale order status changes
- **Manual SMS Sending**: Direct SMS sending capability with template support
- **Mass SMS Campaigns**: Bulk SMS to customer groups and categories
- **Permission Management**: Comprehensive SMS server permission validation and automatic fixing
- **Queue Management**: Reliable SMS queue processing and delivery tracking
- **History Tracking**: Complete audit trail of all SMS communications
- **Template System**: Customizable SMS templates with dynamic field substitution
- **Test Framework**: Organized test suite for comprehensive module validation

---

## Module Architecture

### Core Components

#### 1. SMS Gateway Integration (`tunisiesms.py`)
- **TunisieSMS Model**: Core SMS gateway configuration and management
- **HTTP/SMPP Support**: Multiple API integration methods
- **Automatic Visibility Fix**: Integrated fix_visibility.py functionality
- **Recursion Prevention**: Context-based safety mechanisms
- **Error Handling**: Comprehensive error management and logging

#### 2. Permission Management
- **Automatic User Access**: All users automatically granted SMS access
- **Shared History**: Unified SMS history visible to all authorized users
- **Database Permissions**: Proper access control via `res_smsserver_group_rel`
- **Cache Management**: Odoo 14 compatible cache invalidation

#### 3. Order Integration (`SaleOrderSMS`)
- **Status-based Triggers**: SMS on order state changes
- **Template Processing**: Dynamic field replacement in SMS content
- **Automatic Execution**: Background SMS processing
- **Error Recovery**: Robust error handling and status tracking

#### 4. Test Framework (`test/` directory)
- **Organized Structure**: All tests in dedicated directory
- **Comprehensive Coverage**: Tests for all module components
- **Automated Testing**: Test runner with reporting capabilities
- **Easy Loading**: Scripts for Docker container integration

---

## Installation & Setup

### Prerequisites
- **Odoo 14.0**: Compatible with Odoo Community Edition 14.0
- **PostgreSQL**: Database backend (11+ recommended)
- **Python 3.6+**: Required for Odoo runtime
- **Docker & Docker Compose**: For containerized deployment
- **TUNISIESMS Account**: Active SMS gateway account with API access

### Container Setup
```bash
# Verify containers are running
docker ps

# Expected containers:
# sms-odoo-1    (Odoo application)
# sms-db-1      (PostgreSQL database)
```

### Module Installation
1. Clone the repository into your Odoo addons directory
2. Update your addons path to include the module location
3. Install the module from Apps menu
4. The module automatically configures SMS permissions for all users

### Directory Structure
```
odoo_SMS_Module/
├── test/                            # Test framework
│   ├── test_runner.py              # Comprehensive test runner
│   ├── load_test_files.sh          # Test loading scripts
│   └── [test files]                # All test files
├── tunisiesms.py                   # Core SMS module
├── wizard/                         # SMS wizards
├── data/                           # Configuration data
├── security/                       # Access control
└── static/                         # Web assets
```

---

## Configuration

### SMS Gateway Setup
1. **Navigate to Settings → SMS → SMS Gateway**
2. **Configure TUNISIESMS credentials:**
   - Gateway URL: `https://api.l2t.io/tn/v0/api/api.aspx`
   - Username: Your TUNISIESMS username
   - Password: Your TUNISIESMS password
   - API Key: Your TUNISIESMS API key

### Automatic SMS Configuration
1. **Enable Automatic SMS System**: Master switch for all automatic triggers
2. **Configure Order Templates**: Set SMS templates for different order states
3. **Set Trigger Conditions**: Enable/disable specific order state triggers
4. **Partner Notification**: Configure admin notifications for new contacts

### Permission Management
- **Automatic Setup**: All users automatically granted SMS access on module install
- **Shared Access**: SMS history visible to all authorized users
- **Manual Refresh**: Use "Refresh User Access" button if needed
- **Database Integrity**: Automatic permission validation and fixing

---

## Features

### 1. Automatic SMS Notifications

#### Order Status SMS
- **Draft Orders**: Welcome message when order is created
- **Quotation Sent**: Confirmation when quotation is sent to customer
- **Order Confirmed**: Notification when order is confirmed (sale state)
- **Order Completed**: Delivery confirmation when order is done
- **Order Cancelled**: Cancellation notification

#### Template Variables
Common variables available in SMS templates:
- `%name%` - Order number (e.g., SO001)
- `%partner_id%` - Customer name
- `%state%` - Order status
- `%amount_total%` - Total order amount
- `%date_order%` - Order date
- `%user_id%` - Salesperson name
- `%mobile%` - Customer mobile number

### 2. Manual SMS Sending

#### Single SMS
- Send individual SMS to specific customers
- Template support with variable substitution
- Real-time delivery confirmation
- History tracking

#### Mass SMS
- Send bulk SMS to customer groups
- Category-based targeting
- Progress tracking
- Delivery reports

### 3. Queue Management

#### SMS Queue Processing
- **Automatic Processing**: Background cron jobs process SMS queue
- **Error Handling**: Failed messages marked with error status
- **Retry Logic**: Automatic retry for failed messages
- **Status Tracking**: Real-time status updates

#### Delivery Tracking
- **Message IDs**: Unique tracking for each SMS
- **Delivery Reports**: DLR (Delivery Report) processing
- **Status Updates**: Real-time delivery status updates
- **History Logging**: Complete audit trail

### 4. Permission System

#### Automatic Visibility Fix
- **Integrated Fix**: Built-in fix_visibility.py functionality
- **Automatic Execution**: Runs automatically when needed
- **Context Safety**: Recursion prevention mechanisms
- **Error Recovery**: Robust error handling

#### Access Control
- **Shared Access**: All users see shared SMS history
- **Permission Validation**: Automatic permission checking
- **Database Security**: Proper access control implementation
- **Cache Management**: Odoo 14 compatible cache handling

---

## Quick Start

### 1. Access Odoo Shell
```bash
docker exec -it sms-odoo-1 odoo shell -d test
```

---

## Testing Framework

### Overview
The module includes a comprehensive testing framework located in the `test/` directory. This framework provides organized test suites, automated test runners, and easy integration with Docker containers.

### Test Directory Structure
```
test/
├── __init__.py                      # Python package initialization
├── README.md                        # Test documentation
├── test_runner.py                   # Comprehensive test runner
├── load_test_files.sh              # Bash loading script
├── load_test_files.bat             # Windows loading script
├── basic_order_sms_test_fixed.py   # Basic order SMS tests
├── test_automatic_refresh.py       # Automatic refresh tests
├── test_database_access.py         # Database access tests
├── test_shared_access.py           # Shared access tests
├── test_shared_access_final.py     # Final shared access tests
├── test_view_refresh.py            # View refresh tests
├── trigger_test.py                 # Trigger tests
├── create_test_sms.py              # Test SMS creation utility
└── final_test.py                   # Final comprehensive tests
```

### Test Categories

#### 1. Basic Functionality Tests
- **Order SMS Tests**: Test automatic SMS sending on order status changes
- **Template Tests**: Verify template variable replacement
- **History Tests**: Validate SMS history creation and visibility

#### 2. Access Control Tests
- **Permission Tests**: Validate user access to SMS functionality
- **Shared Access Tests**: Test shared SMS history functionality
- **Database Tests**: Verify proper database permissions

#### 3. View Refresh Tests
- **Automatic Refresh**: Test automatic view refresh mechanisms
- **Cache Tests**: Validate cache invalidation
- **Real-time Updates**: Test live view updates

#### 4. Integration Tests
- **Module Integration**: Test complete module functionality
- **Error Handling**: Validate error recovery mechanisms
- **Performance Tests**: Test under various load conditions

### Running Tests

#### Quick Start
1. **Load tests to container:**
   ```bash
   cd test
   ./load_test_files.sh    # Linux/Mac
   # or
   load_test_files.bat     # Windows
   ```

2. **Access Odoo shell:**
   ```bash
   docker exec -it sms-odoo-1 odoo shell -d odoo
   ```

3. **Run comprehensive test suite:**
   ```python
   exec(open('/tmp/test_runner.py').read())
   run_test_suite()
   ```

#### Advanced Testing

##### Run Specific Tests
```python
# Run specific test file
run_specific_test('test_database_access.py')

# List available tests
list_available_tests()
```

##### Individual Test Files
```python
# Database access test
exec(open('/tmp/test_database_access.py').read())

# Shared access test
exec(open('/tmp/test_shared_access_final.py').read())

# Basic order SMS test
exec(open('/tmp/basic_order_sms_test_fixed.py').read())
```

### Test Results Analysis

#### Success Criteria
- ✅ All tests pass without errors
- ✅ SMS sending returns `Result: True`
- ✅ SMS queue shows new entries
- ✅ History records are created and visible
- ✅ No permission errors occur
- ✅ Automatic visibility fixes work correctly

#### Common Issues and Solutions
1. **Permission Errors**: Automatic visibility fix resolves most permission issues
2. **Empty History**: Test the shared access functionality
3. **SMS Send Failures**: Check gateway configuration and credentials
4. **View Refresh Issues**: Run view refresh tests

---

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

## Appendix

### Module Information
- **Module Name**: Odoo SMS Module
- **Version**: 14.0.0.0 
- **Last Updated**: July 18, 2025
- **Odoo Compatibility**: 14.0
- **SMS Gateway**: TUNISIESMS Integration
- **Test Framework**: Comprehensive test suite included

### Key Improvements
- **Automatic Visibility Fix**: Integrated fix_visibility.py functionality
- **Recursion Prevention**: Context-based safety mechanisms
- **Organized Testing**: All tests moved to dedicated test/ directory
- **Comprehensive Documentation**: Updated for current module state
- **Enhanced Error Handling**: Robust error recovery mechanisms

### Repository Information
- **Repository**: odoo_SMS_Module
- **Owner**: MohamedRayeneRomdhane
- **Branch**: main
- **Test Directory**: `/test/` with organized test suite

---

*This documentation reflects the current state of the Odoo SMS Module with all recent improvements and the organized test framework.*
