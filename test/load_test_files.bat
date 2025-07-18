@echo off
REM Load Test Files Script - Windows Batch Version
REM ==============================================
REM This script copies all SMS test files from the test directory to the Docker container's /tmp directory
REM for easy access and execution within the Odoo environment.

echo === Loading SMS Test Files to Container ===
echo Container: sms-odoo-1
echo Target directory: /tmp/
echo.

set BASE_DIR=c:\Users\facer\OneDrive\Bureau\Backup\sec\odoo\v14\sms\addons\odoo_SMS_Module\test

echo 📂 Copying test files to container...
echo.

REM Copy each test file from the test directory
echo 📄 Copying basic_order_sms_test_fixed.py...
docker cp "%BASE_DIR%\basic_order_sms_test_fixed.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ basic_order_sms_test_fixed.py copied successfully
) else (
    echo    ❌ Failed to copy basic_order_sms_test_fixed.py
)
echo.

echo 📄 Copying test_automatic_refresh.py...
docker cp "%BASE_DIR%\test_automatic_refresh.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ test_automatic_refresh.py copied successfully
) else (
    echo    ❌ Failed to copy test_automatic_refresh.py
)
echo.

echo 📄 Copying test_database_access.py...
docker cp "%BASE_DIR%\test_database_access.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ test_database_access.py copied successfully
) else (
    echo    ❌ Failed to copy test_database_access.py
)
echo.

echo 📄 Copying test_shared_access.py...
docker cp "%BASE_DIR%\test_shared_access.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ test_shared_access.py copied successfully
) else (
    echo    ❌ Failed to copy test_shared_access.py
)
echo.

echo 📄 Copying test_shared_access_final.py...
docker cp "%BASE_DIR%\test_shared_access_final.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ test_shared_access_final.py copied successfully
) else (
    echo    ❌ Failed to copy test_shared_access_final.py
)
echo.

echo 📄 Copying test_view_refresh.py...
docker cp "%BASE_DIR%\test_view_refresh.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ test_view_refresh.py copied successfully
) else (
    echo    ❌ Failed to copy test_view_refresh.py
)
echo.

echo 📄 Copying trigger_test.py...
docker cp "%BASE_DIR%\trigger_test.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ trigger_test.py copied successfully
) else (
    echo    ❌ Failed to copy trigger_test.py
)
echo.

echo 📄 Copying create_test_sms.py...
docker cp "%BASE_DIR%\create_test_sms.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ create_test_sms.py copied successfully
) else (
    echo    ❌ Failed to copy create_test_sms.py
)
echo.

echo 📄 Copying final_test.py...
docker cp "%BASE_DIR%\final_test.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ final_test.py copied successfully
) else (
    echo    ❌ Failed to copy final_test.py
)
echo.

echo 📄 Copying test_runner.py...
docker cp "%BASE_DIR%\test_runner.py" sms-odoo-1:/tmp/
if %errorlevel% equ 0 (
    echo    ✅ test_runner.py copied successfully
) else (
    echo    ❌ Failed to copy test_runner.py
)
echo.

echo 📋 Setting permissions on copied files...
docker exec -it sms-odoo-1 chmod +x /tmp/*.py
echo    ✅ Permissions set
echo.

echo 🔍 Verifying copied files in container...
docker exec -it sms-odoo-1 ls -la /tmp/*.py
echo.

echo 📖 Usage Instructions:
echo =====================
echo.
echo 1. Access Odoo shell:
echo    docker exec -it sms-odoo-1 odoo shell -d odoo
echo.
echo 2. Run any test file:
echo    exec(open('/tmp/basic_order_sms_test_fixed.py').read())
echo    exec(open('/tmp/test_automatic_refresh.py').read())
echo    exec(open('/tmp/test_database_access.py').read())
echo    exec(open('/tmp/test_shared_access.py').read())
echo    exec(open('/tmp/test_shared_access_final.py').read())
echo    exec(open('/tmp/test_view_refresh.py').read())
echo    exec(open('/tmp/trigger_test.py').read())
echo    exec(open('/tmp/create_test_sms.py').read())
echo    exec(open('/tmp/final_test.py').read())
echo.
echo 3. Use the test runner for comprehensive testing:
echo    exec(open('/tmp/test_runner.py').read())
echo    run_test_suite()                    # Run all tests
echo    run_specific_test('test_name.py')   # Run specific test
echo    list_available_tests()              # Show available tests
echo.
echo 4. Or run specific test functions (refer to individual test files for available functions)
echo.
echo 5. Debug SMS functionality:
echo    exec(open('/tmp/test_database_access.py').read())
echo    exec(open('/tmp/test_shared_access_final.py').read())
echo.
echo ✅ All test files loaded successfully!
echo === Script Complete ===

pause
