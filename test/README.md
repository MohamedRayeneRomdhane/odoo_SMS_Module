# SMS Module Test Directory

This directory contains all test files and utilities for the Odoo SMS Module.

## Test Files

### Core Test Files
- `basic_order_sms_test_fixed.py` - Tests for basic order SMS functionality with automatic visibility fix integration
- `test_automatic_refresh.py` - Tests for automatic view refresh functionality
- `test_database_access.py` - Tests for database access permissions
- `test_shared_access.py` - Tests for shared access functionality
- `test_shared_access_final.py` - Final comprehensive shared access tests
- `test_view_refresh.py` - Tests for view refresh mechanisms
- `trigger_test.py` - Tests for SMS trigger functionality
- `create_test_sms.py` - Utility to create test SMS records
- `final_test.py` - Final comprehensive test suite

### Test Loading Scripts
- `load_test_files.sh` - Bash script to load all test files to Docker container
- `load_test_files.bat` - Windows batch script to load all test files to Docker container

## Directory Structure

```
test/
├── __init__.py                      # Python package initialization
├── README.md                        # This file
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

## Usage

### Loading Tests to Container

**On Windows:**
```bash
cd test
load_test_files.bat
```

**On Linux/macOS:**
```bash
cd test
./load_test_files.sh
```

### Running Tests in Odoo Shell

1. Access the Odoo shell:
```bash
docker exec -it sms-odoo-1 odoo shell -d odoo
```

2. Run any test file:
```python
exec(open('/tmp/basic_order_sms_test_fixed.py').read())
exec(open('/tmp/test_automatic_refresh.py').read())
exec(open('/tmp/test_database_access.py').read())
# ... etc
```

3. Or run specific test functions (refer to individual test files for available functions)

## Test Categories

### 1. Basic Functionality Tests
- Order SMS creation and sending
- Template variable replacement
- SMS history creation

### 2. Access Control Tests
- User permission validation
- Shared access functionality
- Database access rights

### 3. View Refresh Tests
- Automatic view refresh mechanisms
- Cache invalidation
- Real-time updates

### 4. Integration Tests
- Module integration testing
- Automatic SMS triggers
- Error handling and recovery

## Notes

- All tests are designed to work with the Odoo 14 SMS Module
- Tests use the integrated automatic visibility fix functionality
- Test files are organized by functionality for easy maintenance
- Load scripts automatically copy all test files to the container for easy access
