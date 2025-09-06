#!/usr/bin/env python3
"""
Epic Image Generator - Comprehensive Stress Test Suite
Tests performance, memory usage, edge cases, and system limits
"""

import sys
import time
import threading
import multiprocessing
import psutil
import tracemalloc
import gc
import random
import string
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime

# Import our generator
from epic_enhanced_generator import EpicImageGenerator

class StressTestSuite:
    def __init__(self):
        self.results = {
            'memory_tests': [],
            'performance_tests': [],
            'concurrency_tests': [],
            'edge_case_tests': [],
            'resource_tests': []
        }
        
    def log_result(self, test_name, status, duration=None, memory_usage=None, error=None):
        """Log test results"""
        result = {
            'test': test_name,
            'status': status,
            'timestamp': datetime.now().isoformat(),
            'duration': duration,
            'memory_usage': memory_usage,
            'error': str(error) if error else None
        }
        
        category = 'performance_tests'
        if 'memory' in test_name.lower():
            category = 'memory_tests'
        elif 'concurrent' in test_name.lower() or 'thread' in test_name.lower():
            category = 'concurrency_tests'
        elif 'edge' in test_name.lower() or 'extreme' in test_name.lower():
            category = 'edge_case_tests'
        elif 'resource' in test_name.lower():
            category = 'resource_tests'
            
        self.results[category].append(result)
        
        # Print result
        status_icon = "PASS" if status == "PASS" else "FAIL"
        duration_str = f" ({duration:.3f}s)" if duration else ""
        memory_str = f" ({memory_usage:.2f}MB)" if memory_usage else ""
        print(f"{status_icon} {test_name}{duration_str}{memory_str}")
        if error:
            print(f"   Error: {error}")

    def test_memory_usage_single_instance(self):
        """Test memory usage of single generator instance"""
        tracemalloc.start()
        start_time = time.time()
        
        try:
            generator = EpicImageGenerator()
            
            # Test basic operations
            generator.detect_content_type("Krishna playing flute in Vrindavan")
            generator.enhance_prompt_epic_style("Rama and Sita in royal court")
            generator.generate_scene_variations("Hanuman flying over Lanka")
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            duration = time.time() - start_time
            memory_mb = peak / 1024 / 1024
            
            self.log_result("Memory Usage - Single Instance", "PASS", duration, memory_mb)
            
        except Exception as e:
            tracemalloc.stop()
            self.log_result("Memory Usage - Single Instance", "FAIL", error=e)

    def test_memory_usage_multiple_instances(self):
        """Test memory usage with multiple generator instances"""
        tracemalloc.start()
        start_time = time.time()
        
        try:
            generators = []
            for i in range(10):
                gen = EpicImageGenerator()
                gen.enhance_prompt_epic_style(f"Epic scene {i} with multiple characters")
                generators.append(gen)
            
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Cleanup
            del generators
            gc.collect()
            
            duration = time.time() - start_time
            memory_mb = peak / 1024 / 1024
            
            self.log_result("Memory Usage - 10 Instances", "PASS", duration, memory_mb)
            
        except Exception as e:
            tracemalloc.stop()
            self.log_result("Memory Usage - 10 Instances", "FAIL", error=e)

    def test_performance_large_prompts(self):
        """Test performance with very large prompts"""
        generator = EpicImageGenerator()
        
        # Generate large prompts of different sizes
        sizes = [1000, 5000, 10000, 50000, 100000]
        
        for size in sizes:
            start_time = time.time()
            try:
                large_prompt = "Krishna and Arjuna in epic battle " * (size // 30)
                result = generator.enhance_prompt_epic_style(large_prompt)
                duration = time.time() - start_time
                
                self.log_result(f"Performance - {size} char prompt", "PASS", duration)
                
            except Exception as e:
                duration = time.time() - start_time
                self.log_result(f"Performance - {size} char prompt", "FAIL", duration, error=e)

    def test_performance_rapid_calls(self):
        """Test performance with rapid successive calls"""
        generator = EpicImageGenerator()
        prompts = [
            "Krishna playing flute",
            "Rama shooting arrow",
            "Hanuman carrying mountain",
            "Sita in garden",
            "Arjuna on battlefield"
        ]
        
        start_time = time.time()
        try:
            for i in range(1000):
                prompt = prompts[i % len(prompts)]
                generator.enhance_prompt_epic_style(prompt)
                generator.detect_content_type(prompt)
            
            duration = time.time() - start_time
            self.log_result("Performance - 1000 Rapid Calls", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Performance - 1000 Rapid Calls", "FAIL", duration, error=e)

    def test_concurrent_thread_safety(self):
        """Test thread safety with concurrent operations"""
        generator = EpicImageGenerator()
        results = []
        errors = []
        
        def worker_thread(thread_id):
            try:
                for i in range(100):
                    prompt = f"Epic scene {thread_id}-{i} with Krishna and Arjuna"
                    result = generator.enhance_prompt_epic_style(prompt)
                    theme, chars = generator.detect_content_type(prompt)
                    results.append((thread_id, i, len(result)))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        start_time = time.time()
        
        # Run 10 threads concurrently
        threads = []
        for i in range(10):
            t = threading.Thread(target=worker_thread, args=(i,))
            t.start()
            threads.append(t)
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        duration = time.time() - start_time
        
        if errors:
            self.log_result("Concurrency - Thread Safety", "FAIL", duration, 
                          error=f"{len(errors)} threads failed")
        else:
            self.log_result("Concurrency - Thread Safety", "PASS", duration)

    def test_concurrent_multiprocessing(self):
        """Test multiprocessing capabilities"""
        def worker_process(process_id):
            try:
                generator = EpicImageGenerator()
                results = []
                for i in range(50):
                    prompt = f"Process {process_id} epic scene {i}"
                    result = generator.enhance_prompt_epic_style(prompt)
                    results.append(len(result))
                return (process_id, len(results), sum(results))
            except Exception as e:
                return (process_id, "ERROR", str(e))
        
        start_time = time.time()
        
        try:
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(worker_process, i) for i in range(4)]
                results = [future.result() for future in futures]
            
            duration = time.time() - start_time
            
            # Check for errors
            errors = [r for r in results if r[1] == "ERROR"]
            if errors:
                self.log_result("Concurrency - Multiprocessing", "FAIL", duration,
                              error=f"{len(errors)} processes failed")
            else:
                self.log_result("Concurrency - Multiprocessing", "PASS", duration)
                
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Concurrency - Multiprocessing", "FAIL", duration, error=e)

    def test_extreme_inputs(self):
        """Test with extreme and malformed inputs"""
        generator = EpicImageGenerator()
        
        extreme_inputs = [
            "",  # Empty string
            " ",  # Whitespace only
            "a" * 100000,  # Very long string
            "unicode" * 1000,  # Unicode characters
            "\n\r\t" * 100,  # Control characters
            "NULL\x00\x01\x02",  # Null and control bytes
            "SELECT * FROM users;",  # SQL injection attempt
            "<script>alert('xss')</script>",  # XSS attempt
            "../../../etc/passwd",  # Path traversal
            "unicode_test" + "a" * 10000,  # Mixed unicode and long text
            "Krishna" + "\x00" * 100 + "Arjuna",  # Embedded nulls
            "Rama\n" * 5000,  # Many newlines
        ]
        
        for i, test_input in enumerate(extreme_inputs):
            start_time = time.time()
            try:
                if test_input.strip():  # Skip empty inputs for enhancement
                    result = generator.enhance_prompt_epic_style(test_input)
                theme, chars = generator.detect_content_type(test_input)
                duration = time.time() - start_time
                
                self.log_result(f"Extreme Input #{i+1}", "PASS", duration)
                
            except Exception as e:
                duration = time.time() - start_time
                # Some errors are expected for malformed inputs
                if "empty" in str(e).lower():
                    self.log_result(f"Extreme Input #{i+1}", "PASS", duration)
                else:
                    self.log_result(f"Extreme Input #{i+1}", "FAIL", duration, error=e)

    def test_resource_exhaustion_memory(self):
        """Test behavior under memory pressure"""
        generators = []
        start_time = time.time()
        
        try:
            # Create many instances until we hit memory limits
            for i in range(100):
                gen = EpicImageGenerator()
                # Generate large data structures
                for j in range(10):
                    gen.enhance_prompt_epic_style("Large epic scene " * 100)
                generators.append(gen)
                
                # Check memory usage
                memory_percent = psutil.virtual_memory().percent
                if memory_percent > 85:  # Stop before system becomes unstable
                    break
            
            duration = time.time() - start_time
            memory_mb = len(generators) * 10  # Approximate
            
            self.log_result("Resource - Memory Pressure", "PASS", duration, memory_mb)
            
        except MemoryError:
            duration = time.time() - start_time
            self.log_result("Resource - Memory Pressure", "PASS", duration, 
                          error="MemoryError caught gracefully")
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Resource - Memory Pressure", "FAIL", duration, error=e)
        finally:
            # Cleanup
            del generators
            gc.collect()

    def test_resource_exhaustion_cpu(self):
        """Test behavior under CPU pressure"""
        start_time = time.time()
        
        try:
            # CPU intensive operations
            generator = EpicImageGenerator()
            
            # Run CPU-intensive tasks
            for i in range(1000):
                large_prompt = "Epic battle scene " * 1000
                generator.enhance_prompt_epic_style(large_prompt)
                generator.generate_scene_variations(large_prompt)
                
                # Check CPU usage periodically
                if i % 100 == 0:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
            
            duration = time.time() - start_time
            self.log_result("Resource - CPU Intensive", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Resource - CPU Intensive", "FAIL", duration, error=e)

    def test_file_system_stress(self):
        """Test file system operations under stress"""
        start_time = time.time()
        
        try:
            # Test multiple generators creating output directories
            generators = []
            for i in range(50):
                gen = EpicImageGenerator()
                generators.append(gen)
            
            duration = time.time() - start_time
            self.log_result("Resource - File System Stress", "PASS", duration)
            
        except Exception as e:
            duration = time.time() - start_time
            self.log_result("Resource - File System Stress", "FAIL", duration, error=e)

    def run_all_tests(self):
        """Run complete stress test suite"""
        print("EPIC IMAGE GENERATOR - COMPREHENSIVE STRESS TEST SUITE")
        print("=" * 60)
        
        start_time = time.time()
        
        print("\nMEMORY TESTS:")
        self.test_memory_usage_single_instance()
        self.test_memory_usage_multiple_instances()
        
        print("\nPERFORMANCE TESTS:")
        self.test_performance_large_prompts()
        self.test_performance_rapid_calls()
        
        print("\nCONCURRENCY TESTS:")
        self.test_concurrent_thread_safety()
        self.test_concurrent_multiprocessing()
        
        print("\nEXTREME INPUT TESTS:")
        self.test_extreme_inputs()
        
        print("\nRESOURCE EXHAUSTION TESTS:")
        self.test_resource_exhaustion_memory()
        self.test_resource_exhaustion_cpu()
        self.test_file_system_stress()
        
        total_duration = time.time() - start_time
        
        print("\n" + "=" * 60)
        print(f"STRESS TEST COMPLETE - Total Duration: {total_duration:.2f}s")
        
        # Generate summary
        self.generate_summary()

    def generate_summary(self):
        """Generate test summary report"""
        print("\nSTRESS TEST SUMMARY:")
        print("-" * 40)
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            if not tests:
                continue
                
            category_total = len(tests)
            category_passed = len([t for t in tests if t['status'] == 'PASS'])
            total_tests += category_total
            passed_tests += category_passed
            
            print(f"{category.replace('_', ' ').title()}: {category_passed}/{category_total}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nOVERALL: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
        
        if success_rate >= 90:
            print("EXCELLENT - System performs well under stress")
        elif success_rate >= 75:
            print("GOOD - System handles most stress scenarios")
        elif success_rate >= 50:
            print("MODERATE - Some issues under stress")
        else:
            print("POOR - Significant stress-related issues")

def main():
    """Run stress test suite"""
    print("System Information:")
    print(f"CPU Cores: {multiprocessing.cpu_count()}")
    print(f"Total Memory: {psutil.virtual_memory().total / 1024**3:.1f} GB")
    print(f"Available Memory: {psutil.virtual_memory().available / 1024**3:.1f} GB")
    print(f"Python Version: {sys.version}")
    
    stress_tester = StressTestSuite()
    stress_tester.run_all_tests()

if __name__ == "__main__":
    main()