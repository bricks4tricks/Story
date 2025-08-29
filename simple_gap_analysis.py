#!/usr/bin/env python3
"""
Simple Security Gap Analysis Tool
Quick analysis of the codebase for remaining security gaps.
"""

import os
import re
from pathlib import Path
from collections import defaultdict


def analyze_security_gaps():
    """Analyze the codebase for security gaps."""
    print("🔍 SECURITY GAP ANALYSIS - LogicAndStories")
    print("=" * 50)
    
    gaps = defaultdict(list)
    current_dir = Path(".")
    
    # 1. Check for remaining XSS vulnerabilities in templates
    print("\n1. 🚨 Checking XSS vulnerabilities...")
    template_files = list(current_dir.glob("templates/*.html"))
    xss_found = 0
    
    for template in template_files:
        try:
            with open(template, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if 'innerHTML' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'innerHTML' in line and 'textContent' not in line:
                            gaps['xss'].append(f"{template}:{i+1} - {line.strip()[:80]}...")
                            xss_found += 1
        except Exception as e:
            print(f"Error reading {template}: {e}")
    
    print(f"   XSS vulnerabilities found: {xss_found}")
    
    # 2. Check for missing CSRF protection
    print("\n2. 🛡️ Checking CSRF protection...")
    python_files = [f for f in current_dir.glob("*.py") if f.is_file()]
    csrf_gaps = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    if '@' in line and 'route(' in line and ('POST' in line or 'PUT' in line or 'DELETE' in line):
                        # Check if CSRF protection exists nearby
                        has_csrf = False
                        for j in range(max(0, i-5), min(len(lines), i+5)):
                            if '@require_csrf' in lines[j]:
                                has_csrf = True
                                break
                        
                        if not has_csrf and 'OPTIONS' not in line:
                            gaps['csrf'].append(f"{py_file}:{i+1} - {line.strip()}")
                            csrf_gaps += 1
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    print(f"   Endpoints missing CSRF protection: {csrf_gaps}")
    
    # 3. Check for hardcoded secrets
    print("\n3. 🔐 Checking for hardcoded secrets...")
    secrets_found = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    if re.search(r'password\s*=\s*["\'][^"\']{5,}["\']', line, re.IGNORECASE):
                        if not any(test in line.lower() for test in ['test', 'example', 'dummy', 'placeholder', 'your_']):
                            gaps['secrets'].append(f"{py_file}:{i+1} - {line.strip()}")
                            secrets_found += 1
        except Exception as e:
            pass
    
    print(f"   Hardcoded secrets found: {secrets_found}")
    
    # 4. Check for dangerous functions
    print("\n4. ⚠️ Checking for dangerous functions...")
    dangerous_found = 0
    dangerous_funcs = ['eval(', 'exec(', 'subprocess.call(', 'os.system(']
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    for func in dangerous_funcs:
                        if func in line:
                            gaps['dangerous'].append(f"{py_file}:{i+1} - {line.strip()}")
                            dangerous_found += 1
        except Exception as e:
            pass
    
    print(f"   Dangerous function calls found: {dangerous_found}")
    
    # 5. Check for input validation gaps
    print("\n5. ✅ Checking input validation...")
    validation_gaps = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    if 'request.' in line and any(method in line for method in ['.get(', '.form', '.args', '.json']):
                        # Check if validation happens nearby
                        has_validation = False
                        for j in range(i, min(len(lines), i+10)):
                            if any(val in lines[j].lower() for val in ['validate', 'sanitize', 'clean']):
                                has_validation = True
                                break
                        
                        if not has_validation and 'get_json(' not in line:
                            validation_gaps += 1
                            if validation_gaps <= 5:  # Limit output
                                gaps['validation'].append(f"{py_file}:{i+1} - {line.strip()}")
        except Exception as e:
            pass
    
    print(f"   Input validation gaps found: {validation_gaps}")
    
    # 6. Generate security score
    print("\n6. 🎯 Security Score Calculation...")
    
    # Calculate penalties
    penalties = {
        'xss': xss_found * 10,      # 10 points per XSS
        'csrf': csrf_gaps * 5,       # 5 points per missing CSRF
        'secrets': secrets_found * 20, # 20 points per hardcoded secret
        'dangerous': dangerous_found * 15, # 15 points per dangerous function
        'validation': min(validation_gaps, 10) * 3  # 3 points per validation gap (max 30)
    }
    
    total_penalty = sum(penalties.values())
    security_score = max(0, 100 - total_penalty)
    
    print(f"   Overall Security Score: {security_score}/100")
    
    # 7. Summary and recommendations
    print("\n" + "=" * 50)
    print("📊 SECURITY GAP ANALYSIS SUMMARY")
    print("=" * 50)
    
    print(f"🚨 XSS Vulnerabilities: {xss_found}")
    print(f"🛡️ Missing CSRF Protection: {csrf_gaps}")
    print(f"🔐 Hardcoded Secrets: {secrets_found}")
    print(f"⚠️  Dangerous Functions: {dangerous_found}")
    print(f"✅ Input Validation Gaps: {validation_gaps}")
    print(f"🎯 Security Score: {security_score}/100")
    
    # Risk assessment
    if security_score >= 90:
        risk_level = "🟢 LOW RISK"
    elif security_score >= 70:
        risk_level = "🟡 MEDIUM RISK"
    elif security_score >= 50:
        risk_level = "🟠 HIGH RISK"
    else:
        risk_level = "🔴 CRITICAL RISK"
    
    print(f"🚦 Overall Risk Level: {risk_level}")
    
    # Priority recommendations
    print("\n🔧 PRIORITY RECOMMENDATIONS:")
    
    if secrets_found > 0:
        print("1. 🚨 CRITICAL: Remove all hardcoded secrets immediately")
    
    if dangerous_found > 0:
        print("2. 🚨 CRITICAL: Review and secure all dangerous function calls")
    
    if xss_found > 0:
        print("3. ⚠️  HIGH: Fix remaining XSS vulnerabilities")
    
    if csrf_gaps > 5:
        print("4. ⚠️  HIGH: Add CSRF protection to unprotected endpoints")
    
    if validation_gaps > 10:
        print("5. 🟡 MEDIUM: Improve input validation coverage")
    
    # Show specific issues (limited)
    if gaps:
        print("\n🔍 SPECIFIC ISSUES FOUND:")
        for category, issues in gaps.items():
            if issues:
                print(f"\n{category.upper()}:")
                for issue in issues[:3]:  # Show first 3 issues per category
                    print(f"  - {issue}")
                if len(issues) > 3:
                    print(f"  ... and {len(issues) - 3} more")
    
    print("\n" + "=" * 50)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 50)
    
    return {
        'xss': xss_found,
        'csrf': csrf_gaps,
        'secrets': secrets_found,
        'dangerous': dangerous_found,
        'validation': validation_gaps,
        'security_score': security_score,
        'risk_level': risk_level,
        'gaps': dict(gaps)
    }


if __name__ == "__main__":
    analyze_security_gaps()