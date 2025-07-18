# 📱 Odoo SMS Module

A comprehensive SMS integration module for Odoo 14 that enables automatic and manual SMS notifications through TUNISIESMS gateway. This module provides seamless SMS functionality for sale orders, customer notifications, and mass messaging capabilities with built-in permission management and automatic visibility fixes.

## 🚀 Key Features

### Core SMS Functionality
- **Automatic SMS Notifications**: Send SMS automatically on sale order status changes
- **Manual SMS Sending**: Send individual SMS messages to customers with template support
- **Mass SMS Campaigns**: Send bulk SMS to customer groups and categories
- **SMS Queue Management**: Reliable SMS queue processing with automatic retry mechanisms
- **SMS History**: Complete audit trail of all SMS communications with shared visibility
- **Template System**: Customizable SMS templates with dynamic field substitution

### Advanced Permission Management
- **Automatic Visibility Fix**: Integrated fix_visibility.py functionality that runs automatically
- **Shared Access**: All authorized users can view complete SMS history
- **Permission Validation**: Automatic permission checking and fixing
- **Recursion Prevention**: Context-based safety mechanisms to prevent infinite loops
- **Database Security**: Proper access control via `res_smsserver_group_rel` table

### TUNISIESMS Gateway Integration
- **HTTP API Integration**: Direct integration with TUNISIESMS REST API
- **Real-time Delivery**: Immediate SMS sending with delivery confirmation
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Authentication**: Secure username/password authentication with TUNISIESMS
- **Delivery Reports**: DLR (Delivery Report) processing for message tracking

### Testing Framework
- **Organized Test Suite**: All tests organized in dedicated `/test/` directory
- **Comprehensive Coverage**: Tests for all module components and features
- **Automated Test Runner**: Built-in test runner with detailed reporting
- **Docker Integration**: Easy test loading scripts for containerized environments
- **Easy Maintenance**: Well-documented test structure for easy updates

## 📁 Module Structure

```
odoo_SMS_Module/
├── test/                            # Testing framework
│   ├── test_runner.py              # Comprehensive test runner
│   ├── load_test_files.sh          # Test loading scripts
│   ├── load_test_files.bat         # Windows test loading
│   ├── README.md                   # Test documentation
│   └── [test files]                # All test files
├── tunisiesms.py                   # Core SMS module
├── wizard/                         # SMS sending wizards
│   ├── single_sms.py              # Individual SMS sending
│   └── mass_sms.py                # Bulk SMS sending
├── data/                           # Configuration data & cron jobs
├── security/                       # Access control
├── static/                         # Web assets & JavaScript
└── views/                          # XML view definitions
```

## 📋 Table of Contents

- [Installation](#installation)
- [Docker Setup](#docker-setup)
- [Configuration](#configuration)
- [Features](#features)
- [Testing](#testing)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Troubleshooting](#troubleshooting)

## 🛠 Installation

### Prerequisites
- **Odoo 14.0**: Compatible with Odoo Community Edition 14.0
- **PostgreSQL**: Database backend (11+ recommended)
- **Python 3.6+**: Required for Odoo runtime
- **Docker & Docker Compose**: For containerized deployment (recommended)
- **TUNISIESMS Account**: Active SMS gateway account with API access

### Quick Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/MohamedRayeneRomdhane/odoo_SMS_Module.git
   cd odoo_SMS_Module
   ```

2. **Install in Odoo:**
   - Copy module to your Odoo addons directory
   - Update your addons path configuration
   - Restart Odoo server
   - Install the module from Apps menu

3. **Automatic Setup:**
   - The module automatically configures SMS permissions for all users
   - Built-in visibility fixes ensure proper access control
   - No manual permission configuration required

## 🐳 Docker Setup

This module includes a complete Docker Compose setup for easy deployment and testing.

### Docker Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Odoo 14.0     │    │  PostgreSQL 11  │
│   Port: 8060    │◄──►│   Port: 5433    │
│   (Container)   │    │   (Container)   │
└─────────────────┘    └─────────────────┘
         ▲
         │
         ▼
┌─────────────────┐
│  SMS Module     │
│  (Volume Mount) │
└─────────────────┘
```

### Docker Compose Configuration

The included `docker-compose.yml` provides:

```yaml
services:
  db:
    image: postgres:11
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo
    volumes:
      - odoo-db:/var/lib/postgresql/data
    ports:
      - "5433:5432"

  odoo:
    build: .
    depends_on:
      - db
    ports:
      - "8060:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./addons:/mnt/extra-addons

volumes:
  odoo-web-data:
  odoo-db:
```

### Quick Start with Docker

#### 1. Clone and Navigate
```bash
git clone https://github.com/MohamedRayeneRomdhane/odoo_SMS_Module.git
cd odoo_SMS_Module
```

#### 2. Build and Start Services
```bash
# Build and start containers
docker-compose up -d

# Check container status
docker-compose ps
```

#### 3. Access Odoo
- **Web Interface**: http://localhost:8060
- **Database**: localhost:5433
- **Default Credentials**: admin/admin (set during first setup)

#### 4. Install SMS Module
1. Go to Apps menu in Odoo
2. Update Apps List
3. Search for "SMS" or "TUNISIESMS"
4. Click Install on the SMS Module

### Docker Environment Details

#### Container Specifications
- **Odoo Container**: 
  - Based on official Odoo 14.0 image
  - Exposed on port 8060 (maps to internal 8069)
  - Auto-restart enabled
  - Volume mounted addons directory

- **PostgreSQL Container**:
  - PostgreSQL 11 official image
  - Exposed on port 5433 (maps to internal 5432)
  - Persistent data storage
  - Optimized for Odoo workloads

#### Volume Management
- **odoo-web-data**: Persistent Odoo data and filestore
- **odoo-db**: PostgreSQL database files
- **./addons**: Local addons directory (including SMS module)

#### Network Configuration
- **Internal Network**: Containers communicate via Docker network
- **External Access**: Web interface on port 8060, database on 5433
- **Service Discovery**: Automatic hostname resolution between services

### Development Setup

#### For Development Work
```bash
# Start in development mode with live reload
docker-compose up

# Access logs
docker-compose logs -f odoo

# Access Odoo shell
docker exec -it sms-odoo-1 odoo shell -d your_database_name

# Restart specific service
docker-compose restart odoo
```

#### For Production Deployment
```bash
# Start in detached mode
docker-compose up -d

# Monitor health
docker-compose ps
docker-compose logs --tail=50 odoo

# Backup database
docker exec sms-db-1 pg_dump -U odoo postgres > backup.sql
```

### Docker Troubleshooting

#### Common Issues
1. **Port Conflicts**: Change ports in docker-compose.yml if 8060/5433 are in use
2. **Permission Issues**: Ensure proper file permissions on ./addons directory
3. **Memory Issues**: Increase Docker memory allocation for large databases
4. **Network Issues**: Check firewall settings for container communication

#### Useful Commands
```bash
# View container logs
docker-compose logs odoo
docker-compose logs db

# Restart services
docker-compose restart

## ⚙️ Configuration

### SMS Gateway Setup

#### 1. Automatic Configuration
The module includes automatic setup features:
- **Auto-Permission Management**: All users automatically granted SMS access
- **Built-in Visibility Fix**: Automatic fixing of permission issues
- **Default Gateway**: Pre-configured TUNISIESMS gateway settings

#### 2. Manual Gateway Configuration (if needed)
- Navigate to: **Settings > Technical > SMS > SMS Gateway**
- Configure TUNISIESMS gateway settings:

```
Name: TUNISIESMS
Method: HTTP
URL: https://api.l2t.io/tn/v0/api/api.aspx
Username: [Your TUNISIESMS Username]
Password: [Your TUNISIESMS Password]
API Key: [Your TUNISIESMS API Key]
Sender: [Your Sender ID]
```

#### 3. Automatic SMS Configuration
- **Enable Automatic SMS System**: Master switch for all automatic triggers
- **Order Templates**: Configure SMS templates for different order states:
  - Draft Order SMS Template
  - Order Confirmed SMS Template  
  - Order Completed SMS Template
  - Order Cancelled SMS Template
- **Trigger Settings**: Enable/disable automatic SMS for specific order states

### Template Variables
Use these variables in your SMS templates:
- `%name%` - Order number (e.g., SO001)
- `%partner_id%` - Customer name
- `%state%` - Order status (draft, sale, done, cancel)
- `%amount_total%` - Total order amount
- `%date_order%` - Order date
- `%user_id%` - Salesperson name
- `%mobile%` - Customer mobile number

### Customer Mobile Number Setup
- **Required Format**: International format without '+' symbol
- **Example**: 21612345678 (Tunisia), 33123456789 (France)
- **Validation**: Module includes mobile number format validation

## 🔧 Features

### 1. Automatic SMS Notifications

#### Order Status Triggers
- **New Orders**: SMS when order is created (draft state)
- **Quotation Sent**: SMS when quotation is sent to customer
- **Order Confirmation**: SMS when order moves to 'sale' state
- **Order Completion**: SMS when order is marked as done
- **Order Cancellation**: SMS when order is cancelled

#### Smart Processing
- **Background Processing**: SMS sent automatically via cron jobs
- **Error Handling**: Failed SMS marked appropriately, don't block processing
- **Status Tracking**: Complete tracking of SMS status per order
- **Template Processing**: Dynamic variable replacement in SMS content

### 2. Manual SMS Sending

#### Single SMS
- **Customer Selection**: Send SMS to specific customers
- **Template Support**: Use predefined templates with variable substitution
- **Real-time Sending**: Immediate SMS delivery
- **History Tracking**: All manual SMS logged in history

#### Mass SMS Campaigns
- **Customer Groups**: Send to specific customer categories
- **Bulk Processing**: Efficient processing of large SMS batches
- **Progress Tracking**: Real-time progress monitoring
- **Delivery Reports**: Comprehensive delivery reporting

### 3. SMS Queue Management

#### Reliable Processing
- **Queue System**: All SMS processed through reliable queue
- **Automatic Retry**: Failed messages automatically retried
- **Batch Processing**: Efficient batch processing (30 messages per batch)
- **Error Isolation**: Failed messages don't affect queue processing

#### Status Management
- **Draft**: SMS queued for sending
- **Sending**: SMS currently being processed
- **Sent**: SMS successfully delivered
- **Error**: SMS failed (with error details)

### 4. Permission Management

#### Automatic Visibility Fix
- **Integrated Solution**: Built-in fix_visibility.py functionality
- **Automatic Execution**: Runs automatically when needed
- **Recursion Prevention**: Context-based safety mechanisms
- **Error Recovery**: Robust error handling and recovery

#### Shared Access
- **Unified History**: All authorized users see complete SMS history
- **Permission Validation**: Automatic permission checking
- **Database Security**: Proper access control implementation
- **Cache Management**: Odoo 14 compatible cache handling

## 🧪 Testing

### Comprehensive Test Framework
The module includes a complete testing framework in the `/test/` directory:

#### Test Organization
```
test/
├── test_runner.py                   # Comprehensive test runner
├── load_test_files.sh              # Test loading for Linux/Mac
├── load_test_files.bat             # Test loading for Windows
├── README.md                       # Test documentation
├── basic_order_sms_test_fixed.py   # Basic functionality tests
├── test_database_access.py         # Database access tests
├── test_shared_access_final.py     # Shared access tests
├── test_automatic_refresh.py       # Auto-refresh tests
└── [additional test files]         # Other specialized tests
```

#### Quick Testing
1. **Load tests to container:**
   ```bash
   cd test
   ./load_test_files.sh    # Linux/Mac
   # or
   load_test_files.bat     # Windows
   ```

2. **Run comprehensive test suite:**
   ```bash
   docker exec -it sms-odoo-1 odoo shell -d odoo
   ```
   ```python
   exec(open('/tmp/test_runner.py').read())
   run_test_suite()
   ```

#### Test Categories
- **Basic Functionality**: Order SMS, template processing, history creation
- **Access Control**: Permission validation, shared access, database security
- **View Refresh**: Automatic refresh mechanisms, cache invalidation
- **Integration**: Complete module functionality, error handling

#### Advanced Testing
```python
# Run specific test
run_specific_test('test_database_access.py')

# List available tests
list_available_tests()

# Individual test execution
exec(open('/tmp/basic_order_sms_test_fixed.py').read())
```

## 📱 Usage

#### Access Method
1. Go to **Contacts** or **Sales > Orders**
2. Select customer or order
3. Click **Action > Send SMS**
4. Choose **Send Single SMS**

#### Single SMS Interface
```
┌─────────────────────────────────┐
│ Send Single SMS                 │
├─────────────────────────────────┤
│ Gateway: [TUNISIESMS ▼]        │
│ Mobile:  [Your number]         │
│ Message: [Your message here]    │
│                                 │
│ [Cancel]  [Send SMS]           │
└─────────────────────────────────┘
```

### Mass SMS Campaigns

#### Access Method
1. Navigate to **SMS > Mass SMS**
2. Click **Create** or use action menu
3. Configure campaign settings

#### Mass SMS Interface
```
┌─────────────────────────────────┐
│ Mass SMS Campaign               │
├─────────────────────────────────┤
│ Gateway: [TUNISIESMS ▼]        │
│ Categories: [Select Categories] │
│ Message: [Campaign message]     │
│                                 │
### Manual SMS Sending

#### Single SMS
1. Navigate to **SMS > Send SMS**
2. Select recipient from customer list
3. Choose or customize SMS template
4. Preview message with variable substitution
5. Send SMS and track delivery status

#### Mass SMS Campaign
1. Navigate to **SMS > Mass SMS**
2. Select customer groups or categories
3. Choose SMS template
4. Configure sending parameters
5. Start campaign and monitor progress

### Automatic Order SMS

#### How It Works
- SMS automatically triggered on order status changes
- Configurable templates for each order state
- Background processing via cron jobs
- Complete error handling and retry logic

#### Order SMS Flow
```
Order Created → Template Processing → SMS Queue → Gateway → Delivery → History
     ↓              ↓                    ↓           ↓          ↓         ↓
  [trigger]    [variables]         [background]  [TUNISIESMS] [DLR]   [audit]
```

#### Template Examples
```
# Order Confirmation
Dear %partner_id%, your order %name% for %amount_total% has been confirmed. 
Expected delivery: %commitment_date%. Thank you for your business!

# Order Completion  
Dear %partner_id%, your order %name% has been completed and delivered. 
Total: %amount_total%. Thank you for choosing us!
```

## 📚 API Reference

### Core Models

#### TunisieSMS (`sms.tunisiesms`)
Main SMS gateway model with automatic permission management.

**Key Methods:**
- `send_msg(data)` - Send SMS through gateway
- `_ensure_all_users_have_access()` - Automatic visibility fix
- `create_test_sms_records()` - Create test records
- `refresh_user_access()` - Manual access refresh

**Configuration Fields:**
- `auto_sms_enabled` - Master switch for automatic SMS
- `order_*_sms` - Templates for different order states
- `status_order_*` - Triggers for automatic SMS

#### Sale Order (`sale.order`)
Enhanced with SMS integration and automatic notifications.

**SMS Fields:**
- `tunisie_sms_status` - SMS sending status
- `tunisie_sms_send_date` - SMS sending timestamp
- `tunisie_sms_msisdn` - Mobile number used

**Methods:**
- `_send_automatic_sms()` - Send automatic SMS
- `action_send_sms_now()` - Manual SMS trigger

### Template Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `%name%` | Order number | SO001 |
| `%partner_id%` | Customer name | John Doe |
| `%state%` | Order status | sale, done |
| `%amount_total%` | Order total | 150.00 |
| `%date_order%` | Order date | 2025-07-18 |
| `%user_id%` | Salesperson | Mitchell Admin |

## 🔧 Troubleshooting

### Common Issues

#### 1. Permission Errors
**Symptom:** "You do not have permission to use gateway"

**Solution:**
```python
# Access Odoo shell and run automatic fix
docker exec -it sms-odoo-1 odoo shell -d odoo
gateway = env['sms.tunisiesms'].search([], limit=1)
gateway._ensure_all_users_have_access()
```

#### 2. Empty SMS History
**Symptom:** SMS history appears empty

**Diagnostic:**
```python
# Check user access
user_id = env.uid
env.cr.execute('SELECT 1 FROM res_smsserver_group_rel WHERE uid = %s', (user_id,))
has_access = bool(env.cr.fetchone())
print(f"User has SMS access: {has_access}")
```

**Solution:** Run shared access test:
```python
exec(open('/tmp/test_shared_access_final.py').read())
```

#### 3. SMS Sending Failures
**Common Causes:**
- Invalid TUNISIESMS credentials
- Insufficient SMS credits
- Invalid mobile number format
- Network connectivity issues

**Diagnostic Steps:**
```python
# Test basic SMS functionality
exec(open('/tmp/basic_order_sms_test_fixed.py').read())

# Check gateway configuration
gateway = env['sms.tunisiesms'].search([], limit=1)
print(f"Gateway URL: {gateway.url}")
print(f"API Key configured: {bool(gateway.key_url_params)}")
```

#### 4. Module Installation Issues
**Symptom:** Infinite recursion during installation

**Solution:** The latest version includes recursion prevention:
- Update to the latest module version
- Restart Odoo and retry installation
- The module now handles installation safely

### Performance Tips

#### 1. Queue Optimization
- Monitor SMS queue regularly for stuck messages
- Ensure cron jobs are running for background processing
- Configure appropriate batch sizes for mass SMS

#### 2. History Management
- Implement periodic cleanup of old SMS history
- Archive old records to maintain performance
- Use database indexes for frequently queried fields

#### 3. Error Monitoring
- Monitor Odoo logs for SMS-related errors
- Set up alerts for failed SMS campaigns
- Regular testing of SMS functionality

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

### Running Tests
```bash
# Load test environment
cd test
./load_test_files.sh

# Run all tests
docker exec -it sms-odoo-1 odoo shell -d odoo
exec(open('/tmp/test_runner.py').read())
run_test_suite()
```

### Code Standards
- Follow Odoo development guidelines
- Include tests for new features
- Update documentation for changes
- Ensure backward compatibility

## 📄 License

This project is licensed under the LGPL-3.0 License - see the LICENSE file for details.

## 🙋‍♂️ Support

### Documentation
- **Complete Documentation**: See `SMS_MODULE_DOCUMENTATION.md`
- **Test Documentation**: See `test/README.md`
- **API Reference**: Included in this README

### Issue Reporting
- Report bugs via GitHub Issues
- Include logs and error messages
- Describe steps to reproduce
- Specify Odoo and module versions

### Contact
- **Repository**: https://github.com/MohamedRayeneRomdhane/odoo_SMS_Module
- **Author**: MohamedRayeneRomdhane
- **Version**: 14.0.0.0

---

## 📊 Module Information

- **Module Version**: 14.0.0.0
- **Odoo Compatibility**: 14.0
- **Last Updated**: July 18, 2025
- **Gateway**: TUNISIESMS Integration
- **Test Framework**: Comprehensive test suite included
- **Permission Management**: Automatic visibility fixes integrated

**Recent Improvements:**
- ✅ Integrated automatic visibility fix functionality
- ✅ Organized test framework in `/test/` directory
- ✅ Context-based recursion prevention
- ✅ Enhanced error handling and recovery
- ✅ Comprehensive documentation updates
- ✅ Robust permission management system

---

*This module provides enterprise-grade SMS functionality with automatic permission management, comprehensive testing, and reliable message delivery through TUNISIESMS gateway.*
5. **Queue Processing**: Verify SMS queue functionality

### Manual Testing

#### Test Customer Setup
- **Name**: Rayen
- **Mobile**: 21621365818
- **Email**: rayen@example.com
- **Location**: Tunis, Tunisia

#### Test Order Creation
1. Create sale order for test customer
2. Add products (Samsung Galaxy Smartphone + Phone Case)
3. Confirm order
4. Verify SMS is triggered and sent

### Testing Documentation

For comprehensive testing procedures, see: [SMS_TESTING_DOCUMENTATION.md](./SMS_TESTING_DOCUMENTATION.md)

## 🔧 Troubleshooting

### Common Issues

#### Permission Errors
**Error**: "You do not have permission to use gateway"
**Solution**: Run permission fix script or add user to SMS server groups

#### SMS Not Sending
**Possible Causes**:
- Invalid gateway credentials
- Insufficient SMS credits
- Wrong mobile number format
- Network connectivity issues

#### Queue Processing Issues
**Symptoms**: SMS stuck in draft state
**Solution**: Manually trigger queue processing or restart SMS services

### Debug Commands

#### Check SMS Status
```python
# Check SMS queue
queue = env['sms.tunisiesms.queue'].search([])
print(f"Queue items: {len(queue)}")

# Check SMS history
history = env['sms.tunisiesms.history'].search([])
print(f"History items: {len(history)}")

# Test gateway connection
gateway = env['sms.tunisiesms'].search([], limit=1)
result = gateway._check_permissions()
print(f"Gateway access: {result}")
```

### Log Analysis

#### Enable SMS Logging
1. Navigate to **Settings > Technical > Logging**
2. Add logger for `odoo.addons.odoo_SMS_Module`
3. Set log level to INFO or DEBUG

#### Log Locations
- **Container Logs**: `docker-compose logs odoo`
- **Odoo Logs**: `/var/log/odoo/odoo-server.log`
- **SMS Module Logs**: Filter by module name

## 📚 API Reference

### SMS Models

#### sms.tunisiesms
Main SMS gateway model
- **Methods**: `send_msg()`, `_check_permissions()`
- **Fields**: `name`, `username`, `password`, `url`, `sender`

#### sms.tunisiesms.queue  
SMS queue management
- **Fields**: `mobile`, `msg`, `state`, `gateway_id`
- **States**: `draft`, `sent`, `error`

#### sms.tunisiesms.history
SMS delivery history
- **Fields**: `mobile`, `msg`, `date`, `state`, `partner_id`

### SMS Methods

#### Send Single SMS
```python
sms_data = {
    'gateway': gateway,
    'mobile_to': '21621365818',
    'text': 'Your message here',
    'validity': 60,
    'classes1': '1',
    'coding': '1',
    'nostop1': False,
}
result = env['sms.tunisiesms'].send_msg(sms_data)
```

#### Process SMS Queue
```python
# Manual queue processing
result = env['sale.order'].process_order_sms_notifications()
```

### Development Environment
```bash
# Set up development environment
git clone https://github.com/MohamedRayeneRomdhane/odoo_SMS_Module.git
cd odoo_SMS_Module
docker-compose up -d
```

## 📄 License

This project is licensed under the LGPL-3.0 License - see the LICENSE file for details.

##  Version History

### v1.2.0 (Current)
- ✅ TUNISIESMS gateway integration
- ✅ Single and mass SMS functionality  
- ✅ Order SMS automation
- ✅ Queue and history management
- ✅ Docker deployment support
- ✅ Comprehensive testing suite

### Roadmap
- 🔄 Multiple SMS gateway support
- 🔄 Advanced template system
- 🔄 SMS scheduling functionality
- 🔄 Analytics and reporting
- 🔄 API webhook integration

---

## 🏷️ Tags

`odoo` `sms` `tunisiesms` `docker` `python` `postgresql` `messaging` `notifications` `automation` `crm`

---

*For detailed testing procedures and troubleshooting, refer to the [SMS Testing Documentation](./SMS_TESTING_DOCUMENTATION.md).*
