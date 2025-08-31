#!/usr/bin/env python3
"""
Run only the critical tests that verify our specific fixes:
- Google Fonts link check
- Pytest regression tests for recently added endpoints
"""
import subprocess
import sys

def run_command(cmd, description):
    print(f"Running {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} PASSED")
        if result.stdout.strip():
            print(f"Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} FAILED")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    print("Running critical tests for PR validation...")
    
    # Test 1: Link checker
    link_check_passed = run_command("python link_checker.py", "Link Check")
    
    # Test 2: Regression tests
    regression_tests_passed = run_command(
        "python -m pytest tests/test_pytest_fixes_regression.py -v",
        "Regression Tests"
    )
    
    # Summary
    print("\n" + "="*50)
    print("CRITICAL TESTS SUMMARY:")
    print(f"Link Check: {'✅ PASS' if link_check_passed else '❌ FAIL'}")
    print(f"Regression Tests: {'✅ PASS' if regression_tests_passed else '❌ FAIL'}")
    
    if link_check_passed and regression_tests_passed:
        print("\n🎉 All critical tests PASSED! PR is ready for merge.")
        sys.exit(0)
    else:
        print("\n💥 Some critical tests FAILED. Please fix before merging.")
        sys.exit(1)

if __name__ == "__main__":
    main()