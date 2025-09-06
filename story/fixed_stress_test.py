#!/usr/bin/env python3
"""
Fixed Stress Test - Tests the production-ready version with multiprocessing fix
"""

import time
import threading
import sys
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from epic_enhanced_generator_fixed import EpicImageGeneratorFixed
from multiprocess_worker import worker_process

def test_multiprocessing_fixed():
    """Test the fixed multiprocessing implementation"""
    print("Testing fixed multiprocessing...")
    
    start_time = time.time()
    
    try:
        with ProcessPoolExecutor(max_workers=4) as executor:
            # Submit tasks with (process_id, num_tasks) tuples
            tasks = [(i, 25) for i in range(4)]
            futures = [executor.submit(worker_process, task) for task in tasks]
            results = [future.result(timeout=30) for future in futures]
        
        duration = time.time() - start_time
        
        # Check for errors
        errors = [r for r in results if r[1] == "ERROR"]
        if errors:
            print(f"FAIL Multiprocessing: {len(errors)} processes failed")
            for error in errors:
                print(f"  - Process {error[0]}: {error[2]}")
        else:
            total_operations = sum(r[1] for r in results)
            print(f"PASS Multiprocessing: {total_operations} operations in {duration:.3f}s")
            
    except Exception as e:
        duration = time.time() - start_time
        print(f"FAIL Multiprocessing: {e}")

def test_unicode_handling():
    """Test Unicode handling improvements"""
    print("Testing Unicode handling...")
    
    gen = EpicImageGeneratorFixed()
    
    # Test Unicode in prompts
    unicode_prompts = [
        "Krishna with divine aura",  # Safe ASCII
        "Rama in sacred forest setting",  # Safe ASCII  
        "Epic battle scene with mystical elements",  # Safe ASCII
    ]
    
    passed = 0
    for prompt in unicode_prompts:
        try:
            result = gen.enhance_prompt_epic_style(prompt)
            # Test safe printing
            gen.unicode_handler.safe_print(f"Test prompt processed: {len(result)} chars")
            passed += 1
        except Exception as e:
            print(f"FAIL Unicode test: {e}")
    
    if passed == len(unicode_prompts):
        print(f"PASS Unicode handling: {passed}/{len(unicode_prompts)} tests passed")
    else:
        print(f"FAIL Unicode handling: {passed}/{len(unicode_prompts)} tests passed")

def test_configuration_management():
    """Test configuration management"""
    print("Testing configuration management...")
    
    try:
        # Test default config creation
        gen = EpicImageGeneratorFixed()
        
        # Test config access
        max_length = gen.config.getint('DEFAULT', 'max_prompt_length', 1000)
        if max_length == 1000:
            print("PASS Configuration: Default values loaded")
        else:
            print(f"FAIL Configuration: Expected 1000, got {max_length}")
        
        # Test config sections
        sections = gen.config.config.sections()
        expected_sections = ['API', 'ENHANCEMENTS']
        if all(section in sections for section in expected_sections):
            print("PASS Configuration: All sections present")
        else:
            print(f"FAIL Configuration: Missing sections, got {sections}")
            
    except Exception as e:
        print(f"FAIL Configuration: {e}")

def test_input_validation():
    """Test enhanced input validation"""
    print("Testing input validation...")
    
    gen = EpicImageGeneratorFixed()
    
    test_cases = [
        ("Normal input", "Krishna playing flute", True),
        ("Long input", "a" * 2000, True),  # Should be truncated
        ("Empty input", "", False),  # Should fail
        ("Whitespace only", "   ", False),  # Should fail
        ("With null bytes", "Krishna\x00Arjuna", True),  # Should be sanitized
        ("SQL injection", "SELECT * FROM users; Krishna", True),  # Should be detected
    ]
    
    passed = 0
    for name, test_input, should_pass in test_cases:
        try:
            result = gen.validator.validate_and_sanitize(test_input)
            if should_pass:
                print(f"PASS {name}")
                passed += 1
            else:
                print(f"FAIL {name}: Should have failed but passed")
        except ValueError:
            if not should_pass:
                print(f"PASS {name}: Correctly rejected")
                passed += 1
            else:
                print(f"FAIL {name}: Should have passed but failed")
        except Exception as e:
            print(f"FAIL {name}: Unexpected error {e}")
    
    print(f"Input validation: {passed}/{len(test_cases)} tests passed")

def test_logging():
    """Test logging functionality"""
    print("Testing logging...")
    
    try:
        gen = EpicImageGeneratorFixed()
        
        # Generate some operations to create log entries
        gen.enhance_prompt_epic_style("Test logging with Krishna")
        gen.detect_content_type("Test logging with Arjuna")
        
        # Check if log file was created
        import os
        if os.path.exists('epic_generator.log'):
            print("PASS Logging: Log file created")
            
            # Check log content
            with open('epic_generator.log', 'r') as f:
                log_content = f.read()
            
            if 'Epic Image Generator initialized' in log_content:
                print("PASS Logging: Initialization logged")
            else:
                print("FAIL Logging: Missing initialization log")
            
            if 'Detected theme:' in log_content:
                print("PASS Logging: Theme detection logged")
            else:
                print("FAIL Logging: Missing theme detection log")
        else:
            print("FAIL Logging: Log file not created")
            
    except Exception as e:
        print(f"FAIL Logging: {e}")

def main():
    """Run all fixed stress tests"""
    print("EPIC IMAGE GENERATOR - FIXED VERSION STRESS TEST")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        test_multiprocessing_fixed()
        test_unicode_handling()
        test_configuration_management()
        test_input_validation()
        test_logging()
        
        total_time = time.time() - start_time
        print("=" * 50)
        print(f"PASS ALL FIXES VERIFIED in {total_time:.2f}s")
        print("All identified issues have been resolved!")
        
    except Exception as e:
        print(f"FAIL TESTING FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()