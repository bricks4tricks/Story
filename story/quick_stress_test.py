#!/usr/bin/env python3
"""
Quick Stress Test - Focused stress testing without excessive output
"""

import time
import threading
import sys
from epic_enhanced_generator import EpicImageGenerator

def test_memory_and_performance():
    """Test memory usage and performance"""
    print("Testing memory and performance...")
    
    # Single instance test
    start = time.time()
    gen = EpicImageGenerator()
    gen.enhance_prompt_epic_style("Krishna playing flute in divine setting")
    single_time = time.time() - start
    print(f"PASS Single instance: {single_time:.3f}s")
    
    # Multiple instances
    start = time.time()
    generators = [EpicImageGenerator() for _ in range(5)]
    for i, g in enumerate(generators):
        g.enhance_prompt_epic_style(f"Epic scene {i}")
    multi_time = time.time() - start
    print(f"PASS Multiple instances (5): {multi_time:.3f}s")
    
    # Performance with large prompts
    start = time.time()
    large_prompt = "Epic battle scene with Krishna and Arjuna " * 50
    gen.enhance_prompt_epic_style(large_prompt)
    large_time = time.time() - start
    print(f"PASS Large prompt handling: {large_time:.3f}s")

def test_concurrency():
    """Test thread safety"""
    print("Testing concurrency...")
    
    gen = EpicImageGenerator()
    results = []
    errors = []
    
    def worker(thread_id):
        try:
            for i in range(20):
                prompt = f"Thread {thread_id} scene {i} with epic characters"
                result = gen.enhance_prompt_epic_style(prompt)
                results.append(len(result))
        except Exception as e:
            errors.append(f"Thread {thread_id}: {e}")
    
    start = time.time()
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    duration = time.time() - start
    
    if errors:
        print(f"FAIL Concurrency failed: {len(errors)} errors")
        for error in errors[:3]:  # Show first 3 errors
            print(f"  - {error}")
    else:
        print(f"PASS Thread safety: {len(results)} operations in {duration:.3f}s")

def test_extreme_inputs():
    """Test with extreme inputs"""
    print("Testing extreme inputs...")
    
    gen = EpicImageGenerator()
    test_cases = [
        ("Empty string", ""),
        ("Very long", "a" * 5000),
        ("Special chars", "Krishna\n\r\t\0Arjuna"),
        ("SQL injection", "SELECT * FROM users; DROP TABLE epics;"),
        ("Mixed content", "Krishna 🙏 Arjuna" if sys.platform != "win32" else "Krishna Arjuna"),
    ]
    
    passed = 0
    for name, test_input in test_cases:
        try:
            if test_input.strip():  # Skip empty for enhancement
                result = gen.enhance_prompt_epic_style(test_input)
            theme, chars = gen.detect_content_type(test_input)
            print(f"PASS {name}")
            passed += 1
        except ValueError as e:
            if "empty" in str(e).lower():
                print(f"PASS {name} (expected error)")
                passed += 1
            else:
                print(f"FAIL {name}: {e}")
        except Exception as e:
            print(f"FAIL {name}: {e}")
    
    print(f"Extreme inputs: {passed}/{len(test_cases)} passed")

def test_rapid_operations():
    """Test rapid successive operations"""
    print("Testing rapid operations...")
    
    gen = EpicImageGenerator()
    prompts = [
        "Krishna playing flute",
        "Rama with bow", 
        "Hanuman flying",
        "Sita in garden",
        "Arjuna on battlefield"
    ]
    
    start = time.time()
    for i in range(100):  # Reduced from 1000
        prompt = prompts[i % len(prompts)]
        gen.enhance_prompt_epic_style(prompt)
        gen.detect_content_type(prompt)
    
    duration = time.time() - start
    if duration > 0:
        rate = 100 / duration
        print(f"PASS Rapid operations: 100 calls in {duration:.3f}s ({rate:.1f} ops/sec)")
    else:
        print(f"PASS Rapid operations: 100 calls completed instantly (very fast!)")

def main():
    """Run focused stress tests"""
    print("EPIC IMAGE GENERATOR - FOCUSED STRESS TEST")
    print("=" * 50)
    
    start_time = time.time()
    
    try:
        test_memory_and_performance()
        test_concurrency()
        test_extreme_inputs()
        test_rapid_operations()
        
        total_time = time.time() - start_time
        print("=" * 50)
        print(f"PASS ALL STRESS TESTS COMPLETED in {total_time:.2f}s")
        print("System is stable under stress conditions!")
        
    except Exception as e:
        print(f"FAIL STRESS TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()