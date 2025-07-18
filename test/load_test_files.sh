#!/bin/bash
"""
Load Test Files Script
======================
This script copies all SMS test files from the test directory to the Docker container's /tmp directory
for easy access and execution within the Odoo environment.
"""

echo "=== Loading SMS Test Files to Container ==="
echo "Container: sms-odoo-1"
echo "Target directory: /tmp/"
echo ""

# Define the base directory (now pointing to the test subdirectory)
BASE_DIR="/c/Users/facer/OneDrive/Bureau/Backup/sec/odoo/v14/sms/addons/odoo_SMS_Module/test"

# Array of test files to copy (all files now in the test directory)
declare -a TEST_FILES=(
    "basic_order_sms_test_fixed.py"
    "test_automatic_refresh.py"
    "test_database_access.py"
    "test_shared_access.py"
    "test_shared_access_final.py"
    "test_view_refresh.py"
    "trigger_test.py"
    "create_test_sms.py"
    "final_test.py"
    "test_runner.py"
)

echo "📂 Copying test files to container..."
echo ""

# Copy each test file
for file in "${TEST_FILES[@]}"; do
    if [ -f "$BASE_DIR/$file" ]; then
        echo "📄 Copying $file..."
        docker cp "$BASE_DIR/$file" sms-odoo-1:/tmp/
        if [ $? -eq 0 ]; then
            echo "   ✅ $file copied successfully"
        else
            echo "   ❌ Failed to copy $file"
        fi
    else
        echo "   ⚠️  $file not found - skipping"
    fi
    echo ""
done

echo "📋 Setting permissions on copied files..."
docker exec -it sms-odoo-1 chmod +x /tmp/*.py
echo "   ✅ Permissions set"
echo ""

echo "🔍 Verifying copied files in container..."
docker exec -it sms-odoo-1 ls -la /tmp/*.py
echo ""

echo "📖 Usage Instructions:"
echo "====================="
echo ""
echo "1. Access Odoo shell:"
echo "   docker exec -it sms-odoo-1 odoo shell -d odoo"
echo ""
echo "2. Run any test file:"
echo "   exec(open('/tmp/basic_order_sms_test_fixed.py').read())"
echo "   exec(open('/tmp/test_automatic_refresh.py').read())"
echo "   exec(open('/tmp/test_database_access.py').read())"
echo "   exec(open('/tmp/test_shared_access.py').read())"
echo "   exec(open('/tmp/test_shared_access_final.py').read())"
echo "   exec(open('/tmp/test_view_refresh.py').read())"
echo "   exec(open('/tmp/trigger_test.py').read())"
echo "   exec(open('/tmp/create_test_sms.py').read())"
echo "   exec(open('/tmp/final_test.py').read())"
echo ""
echo "3. Use the test runner for comprehensive testing:"
echo "   exec(open('/tmp/test_runner.py').read())"
echo "   run_test_suite()                    # Run all tests"
echo "   run_specific_test('test_name.py')   # Run specific test"
echo "   list_available_tests()              # Show available tests"
echo ""
echo "4. Or run specific test functions (refer to individual test files for available functions)"
echo ""
echo "5. Debug SMS functionality:"
echo "   exec(open('/tmp/test_database_access.py').read())"
echo "   exec(open('/tmp/test_shared_access_final.py').read())"
echo ""
echo "✅ All test files loaded successfully!"
echo "=== Script Complete ==="
