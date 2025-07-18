#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SMS Module Test Runner
=====================
This script runs all SMS module tests in sequence and provides a comprehensive report.
"""

import logging
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

logger = logging.getLogger(__name__)

def run_test_suite():
    """Run the complete SMS module test suite."""
    logger.info("🚀 Starting SMS Module Test Suite")
    logger.info("=" * 50)
    
    test_files = [
        'test_database_access.py',
        'test_shared_access.py', 
        'test_view_refresh.py',
        'test_automatic_refresh.py',
        'basic_order_sms_test_fixed.py',
        'trigger_test.py',
        'create_test_sms.py',
        'test_shared_access_final.py',
        'final_test.py'
    ]
    
    results = {
        'passed': 0,
        'failed': 0,
        'total': len(test_files),
        'details': []
    }
    
    for test_file in test_files:
        logger.info(f"🧪 Running test: {test_file}")
        
        try:
            # Execute the test file
            with open(f'/tmp/{test_file}', 'r') as f:
                test_code = f.read()
            
            # Create a test execution context
            test_context = {
                '__name__': '__main__',
                'logger': logger
            }
            
            # Add env if available in global scope
            if 'env' in globals():
                test_context['env'] = globals()['env']
            
            # Execute the test
            exec(test_code, test_context)
            
            results['passed'] += 1
            results['details'].append({
                'test': test_file,
                'status': 'PASSED',
                'message': 'Test executed successfully'
            })
            logger.info(f"✅ {test_file} - PASSED")
            
        except Exception as e:
            results['failed'] += 1
            results['details'].append({
                'test': test_file,
                'status': 'FAILED',
                'message': str(e)
            })
            logger.error(f"❌ {test_file} - FAILED: {str(e)}")
    
    # Generate summary report
    logger.info("=" * 50)
    logger.info("📊 TEST SUMMARY REPORT")
    logger.info("=" * 50)
    logger.info(f"Total Tests: {results['total']}")
    logger.info(f"Passed: {results['passed']}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Success Rate: {(results['passed'] / results['total']) * 100:.1f}%")
    
    # Detailed results
    logger.info("=" * 50)
    logger.info("📋 DETAILED RESULTS")
    logger.info("=" * 50)
    
    for detail in results['details']:
        status_emoji = "✅" if detail['status'] == 'PASSED' else "❌"
        logger.info(f"{status_emoji} {detail['test']}: {detail['status']}")
        if detail['status'] == 'FAILED':
            logger.info(f"   Error: {detail['message']}")
    
    logger.info("=" * 50)
    logger.info("🏁 Test Suite Complete")
    logger.info("=" * 50)
    
    return results

def run_specific_test(test_name):
    """Run a specific test by name."""
    logger.info(f"🧪 Running specific test: {test_name}")
    
    try:
        with open(f'/tmp/{test_name}', 'r') as f:
            test_code = f.read()
        
        test_context = {
            '__name__': '__main__',
            'logger': logger
        }
        
        # Add env if available in global scope
        if 'env' in globals():
            test_context['env'] = globals()['env']
        
        exec(test_code, test_context)
        logger.info(f"✅ {test_name} - PASSED")
        return True
        
    except Exception as e:
        logger.error(f"❌ {test_name} - FAILED: {str(e)}")
        return False

def list_available_tests():
    """List all available test files."""
    logger.info("📋 Available Test Files:")
    logger.info("=" * 30)
    
    test_files = [
        'basic_order_sms_test_fixed.py',
        'test_automatic_refresh.py',
        'test_database_access.py',
        'test_shared_access.py',
        'test_shared_access_final.py',
        'test_view_refresh.py',
        'trigger_test.py',
        'create_test_sms.py',
        'final_test.py'
    ]
    
    for i, test_file in enumerate(test_files, 1):
        logger.info(f"{i:2d}. {test_file}")
    
    logger.info("=" * 30)
    logger.info("Usage examples:")
    logger.info("  run_test_suite()                    # Run all tests")
    logger.info("  run_specific_test('test_name.py')   # Run specific test")
    logger.info("  list_available_tests()              # Show this list")

if __name__ == '__main__':
    # Auto-run when executed directly
    logger.info("SMS Module Test Runner loaded successfully!")
    logger.info("Available commands:")
    logger.info("  run_test_suite()     - Run all tests")
    logger.info("  run_specific_test()  - Run specific test")
    logger.info("  list_available_tests() - List available tests")
