#!/usr/bin/env python3
"""
Automated Security Gap Analysis Tool
Analyzes the codebase for security gaps and generates detailed reports with visualizations.
"""

import os
import re
import json
import ast
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Any
import subprocess


class SecurityGapAnalyzer:
    """Comprehensive security gap analysis tool."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.gaps = defaultdict(list)
        self.security_scores = {}
        self.file_risks = {}
        
    def analyze_xss_vulnerabilities(self) -> Dict[str, List[Dict]]:
        """Analyze potential XSS vulnerabilities."""
        xss_gaps = []
        
        # Check HTML templates for unsafe patterns
        template_files = list(self.project_root.glob("templates/*.html"))
        
        for template in template_files:
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Check for remaining innerHTML usage
                    if 'innerHTML' in line and 'textContent' not in line:
                        xss_gaps.append({
                            'file': str(template),
                            'line': i + 1,
                            'issue': 'Potential XSS via innerHTML',
                            'severity': 'HIGH',
                            'code': line.strip()
                        })
                    
                    # Check for unescaped template variables
                    if re.search(r'\{\{[^}]*\|safe\}\}', line):
                        xss_gaps.append({
                            'file': str(template),
                            'line': i + 1,
                            'issue': 'Unsafe template variable',
                            'severity': 'MEDIUM',
                            'code': line.strip()
                        })
                    
                    # Check for dangerous event handlers
                    if re.search(r'on\w+\s*=\s*["\'][^"\']*["\']', line):
                        xss_gaps.append({
                            'file': str(template),
                            'line': i + 1,
                            'issue': 'Inline event handler',
                            'severity': 'MEDIUM',
                            'code': line.strip()
                        })
        
        self.gaps['xss'] = xss_gaps
        return {'xss_vulnerabilities': xss_gaps}
    
    def analyze_sql_injection_risks(self) -> Dict[str, List[Dict]]:
        """Analyze potential SQL injection vulnerabilities."""
        sql_gaps = []
        
        python_files = list(self.project_root.glob("*.py"))
        
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Check for string formatting in SQL
                    if re.search(r'f["\']\s*(?:SELECT|INSERT|UPDATE|DELETE).*\{.*\}.*["\']', line, re.IGNORECASE):
                        sql_gaps.append({
                            'file': str(py_file),
                            'line': i + 1,
                            'issue': 'SQL injection via f-string',
                            'severity': 'CRITICAL',
                            'code': line.strip()
                        })
                    
                    # Check for .format() in SQL
                    if re.search(r'["\'].*(?:SELECT|INSERT|UPDATE|DELETE).*["\']\.format\(', line, re.IGNORECASE):
                        sql_gaps.append({
                            'file': str(py_file),
                            'line': i + 1,
                            'issue': 'SQL injection via .format()',
                            'severity': 'HIGH',
                            'code': line.strip()
                        })
                    
                    # Check for string concatenation in SQL
                    if re.search(r'["\'].*(?:SELECT|INSERT|UPDATE|DELETE).*["\'].*\+.*["\']', line, re.IGNORECASE):
                        sql_gaps.append({
                            'file': str(py_file),
                            'line': i + 1,
                            'issue': 'SQL injection via concatenation',
                            'severity': 'HIGH',
                            'code': line.strip()
                        })
        
        self.gaps['sql_injection'] = sql_gaps
        return {'sql_injection_risks': sql_gaps}
    
    def analyze_authentication_gaps(self) -> Dict[str, List[Dict]]:
        """Analyze authentication and authorization gaps."""
        auth_gaps = []
        
        # Check for missing authentication decorators
        python_files = list(self.project_root.glob("*.py"))
        
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                in_route_function = False
                has_auth_decorator = False
                route_line = 0
                
                for i, line in enumerate(lines):
                    # Check for route decorators
                    if re.search(r'@\w+\.route\(.*methods.*=.*\[.*["\'](?:POST|PUT|DELETE)["\']', line):
                        in_route_function = True
                        route_line = i + 1
                        has_auth_decorator = False
                        
                        # Check for authentication decorators in surrounding lines
                        for j in range(max(0, i-5), min(len(lines), i+3)):
                            if '@require_auth' in lines[j] or '@login_required' in lines[j]:
                                has_auth_decorator = True
                                break
                    
                    # Check if we're at the function definition
                    elif in_route_function and line.strip().startswith('def '):
                        if not has_auth_decorator:
                            auth_gaps.append({
                                'file': str(py_file),
                                'line': route_line,
                                'issue': 'State-changing endpoint without authentication',
                                'severity': 'HIGH',
                                'code': lines[route_line-1].strip()
                            })
                        in_route_function = False
        
        # Check for hardcoded credentials
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Check for hardcoded passwords
                    if re.search(r'password\s*=\s*["\'][^"\']{3,}["\']', line, re.IGNORECASE):
                        if not any(test in line.lower() for test in ['test', 'example', 'dummy', 'placeholder']):
                            auth_gaps.append({
                                'file': str(py_file),
                                'line': i + 1,
                                'issue': 'Hardcoded password',
                                'severity': 'CRITICAL',
                                'code': line.strip()
                            })
        
        self.gaps['authentication'] = auth_gaps
        return {'authentication_gaps': auth_gaps}
    
    def analyze_input_validation_gaps(self) -> Dict[str, List[Dict]]:
        """Analyze input validation gaps."""
        validation_gaps = []
        
        python_files = list(self.project_root.glob("*.py"))
        
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Check for direct request.args/form usage without validation
                    if re.search(r'request\.(args|form|json)\.get\(["\'][^"\']+["\'](?:,.*?)?\)', line):
                        # Check if validation happens nearby
                        validation_found = False
                        for j in range(i, min(len(lines), i+5)):
                            if any(val_func in lines[j] for val_func in ['validate', 'sanitize', 'clean', 'escape']):
                                validation_found = True
                                break
                        
                        if not validation_found:
                            validation_gaps.append({
                                'file': str(py_file),
                                'line': i + 1,
                                'issue': 'User input without validation',
                                'severity': 'MEDIUM',
                                'code': line.strip()
                            })
                    
                    # Check for eval() usage (dangerous)
                    if 'eval(' in line:
                        validation_gaps.append({
                            'file': str(py_file),
                            'line': i + 1,
                            'issue': 'Dangerous eval() usage',
                            'severity': 'CRITICAL',
                            'code': line.strip()
                        })
                    
                    # Check for exec() usage
                    if 'exec(' in line:
                        validation_gaps.append({
                            'file': str(py_file),
                            'line': i + 1,
                            'issue': 'Dangerous exec() usage',
                            'severity': 'CRITICAL',
                            'code': line.strip()
                        })
        
        self.gaps['input_validation'] = validation_gaps
        return {'input_validation_gaps': validation_gaps}
    
    def analyze_csrf_protection_gaps(self) -> Dict[str, List[Dict]]:
        """Analyze CSRF protection gaps."""
        csrf_gaps = []
        
        python_files = list(self.project_root.glob("*.py"))
        
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Check for POST/PUT/DELETE routes without CSRF protection
                    if re.search(r'@\w+\.route\(.*methods.*=.*\[.*["\'](?:POST|PUT|DELETE)["\']', line):
                        has_csrf = False
                        
                        # Check for CSRF decorator in surrounding lines
                        for j in range(max(0, i-5), min(len(lines), i+5)):
                            if '@require_csrf' in lines[j] or '@csrf.protect' in lines[j]:
                                has_csrf = True
                                break
                        
                        if not has_csrf:
                            csrf_gaps.append({
                                'file': str(py_file),
                                'line': i + 1,
                                'issue': 'State-changing endpoint without CSRF protection',
                                'severity': 'HIGH',
                                'code': line.strip()
                            })
        
        self.gaps['csrf'] = csrf_gaps
        return {'csrf_protection_gaps': csrf_gaps}
    
    def analyze_file_security_gaps(self) -> Dict[str, List[Dict]]:
        """Analyze file handling security gaps."""
        file_gaps = []
        
        python_files = list(self.project_root.glob("*.py"))
        
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines):
                    # Check for file operations without validation
                    if 'request.files' in line:
                        # Check if security validation is present nearby
                        security_found = False
                        for j in range(i, min(len(lines), i+10)):
                            if any(sec in lines[j] for sec in ['secure_filename', 'validate', 'MIME', 'file_security']):
                                security_found = True
                                break
                        
                        if not security_found:
                            file_gaps.append({
                                'file': str(py_file),
                                'line': i + 1,
                                'issue': 'File upload without security validation',
                                'severity': 'HIGH',
                                'code': line.strip()
                            })
                    
                    # Check for open() calls with user input
                    if re.search(r'open\([^)]*\+[^)]*\)', line) or re.search(r'open\(.*request\.|open\(.*input\(', line):
                        file_gaps.append({
                            'file': str(py_file),
                            'line': i + 1,
                            'issue': 'File operation with user input',
                            'severity': 'MEDIUM',
                            'code': line.strip()
                        })
        
        self.gaps['file_security'] = file_gaps
        return {'file_security_gaps': file_gaps}
    
    def analyze_logging_monitoring_gaps(self) -> Dict[str, List[Dict]]:
        """Analyze logging and monitoring gaps."""
        logging_gaps = []
        
        # Check if security logging is implemented
        python_files = list(self.project_root.glob("*.py"))
        
        has_security_logging = False
        has_monitoring = False
        
        for py_file in python_files:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                if 'security' in content.lower() and 'log' in content.lower():
                    has_security_logging = True
                
                if any(monitor in content.lower() for monitor in ['prometheus', 'metrics', 'monitoring']):
                    has_monitoring = True
        
        if not has_security_logging:
            logging_gaps.append({
                'file': 'Global',
                'line': 0,
                'issue': 'No security event logging implemented',
                'severity': 'HIGH',
                'code': 'Missing security logging framework'
            })
        
        if not has_monitoring:
            logging_gaps.append({
                'file': 'Global',
                'line': 0,
                'issue': 'No security monitoring implemented',
                'severity': 'MEDIUM',
                'code': 'Missing monitoring/alerting system'
            })
        
        self.gaps['logging'] = logging_gaps
        return {'logging_monitoring_gaps': logging_gaps}
    
    def calculate_security_scores(self) -> Dict[str, float]:
        """Calculate security scores for different components."""
        scores = {}
        
        # Calculate scores based on gap severity
        severity_weights = {'CRITICAL': 10, 'HIGH': 5, 'MEDIUM': 2, 'LOW': 1}
        max_score = 100
        
        for category, gaps in self.gaps.items():
            penalty = sum(severity_weights.get(gap['severity'], 1) for gap in gaps)
            score = max(0, max_score - penalty)
            scores[category] = score
        
        # Overall security score
        if scores:
            scores['overall'] = sum(scores.values()) / len(scores)
        else:
            scores['overall'] = max_score
        
        self.security_scores = scores
        return scores
    
    def generate_risk_matrix(self) -> Dict[str, Any]:
        """Generate risk matrix data."""
        risk_matrix = {
            'components': ['Authentication', 'Input Validation', 'File Upload', 'CSRF Protection', 'XSS Prevention'],
            'risks': ['SQL Injection', 'XSS Attacks', 'File Attacks', 'CSRF Attacks', 'Auth Bypass'],
            'matrix': []
        }
        
        # Generate risk scores for each component-risk combination
        for component in risk_matrix['components']:
            row = []
            for risk in risk_matrix['risks']:
                # Calculate risk score based on gaps found
                category = component.lower().replace(' ', '_')
                gaps = self.gaps.get(category, [])
                
                if gaps:
                    avg_severity = sum(3 if g['severity'] == 'CRITICAL' else 
                                     2 if g['severity'] == 'HIGH' else 1 
                                     for g in gaps) / len(gaps)
                    risk_score = min(5, int(avg_severity) + len(gaps))
                else:
                    risk_score = 1  # Low risk if no gaps found
                
                row.append(risk_score)
            
            risk_matrix['matrix'].append(row)
        
        return risk_matrix
    
    def run_full_analysis(self) -> Dict[str, Any]:
        """Run comprehensive security gap analysis."""
        print("🔍 Starting Comprehensive Security Gap Analysis...")
        
        results = {}
        
        # Run all analysis modules
        print("Analyzing XSS vulnerabilities...")
        results.update(self.analyze_xss_vulnerabilities())
        
        print("Analyzing SQL injection risks...")
        results.update(self.analyze_sql_injection_risks())
        
        print("Analyzing authentication gaps...")
        results.update(self.analyze_authentication_gaps())
        
        print("Analyzing input validation gaps...")
        results.update(self.analyze_input_validation_gaps())
        
        print("Analyzing CSRF protection gaps...")
        results.update(self.analyze_csrf_protection_gaps())
        
        print("Analyzing file security gaps...")
        results.update(self.analyze_file_security_gaps())
        
        print("Analyzing logging/monitoring gaps...")
        results.update(self.analyze_logging_monitoring_gaps())
        
        print("Calculating security scores...")
        results['security_scores'] = self.calculate_security_scores()
        
        print("Generating risk matrix...")
        results['risk_matrix'] = self.generate_risk_matrix()
        
        # Generate summary statistics
        total_gaps = sum(len(gaps) for gaps in self.gaps.values())
        critical_gaps = sum(1 for gaps in self.gaps.values() 
                           for gap in gaps if gap['severity'] == 'CRITICAL')
        high_gaps = sum(1 for gaps in self.gaps.values() 
                       for gap in gaps if gap['severity'] == 'HIGH')
        
        results['summary'] = {
            'total_gaps': total_gaps,
            'critical_gaps': critical_gaps,
            'high_gaps': high_gaps,
            'overall_score': results['security_scores'].get('overall', 0),
            'analyzed_files': len(list(self.project_root.glob("*.py"))) + len(list(self.project_root.glob("templates/*.html")))
        }
        
        return results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate detailed security gap analysis report."""
        report = []
        report.append("# 🛡️ AUTOMATED SECURITY GAP ANALYSIS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary
        summary = results['summary']
        report.append("## 📊 EXECUTIVE SUMMARY")
        report.append(f"- **Total Security Gaps Found**: {summary['total_gaps']}")
        report.append(f"- **Critical Issues**: {summary['critical_gaps']}")
        report.append(f"- **High Priority Issues**: {summary['high_gaps']}")
        report.append(f"- **Overall Security Score**: {summary['overall_score']:.1f}/100")
        report.append(f"- **Files Analyzed**: {summary['analyzed_files']}")
        report.append("")
        
        # Detailed findings by category
        categories = {
            'xss_vulnerabilities': '🚨 XSS Vulnerabilities',
            'sql_injection_risks': '💉 SQL Injection Risks',
            'authentication_gaps': '🔐 Authentication Gaps',
            'input_validation_gaps': '✅ Input Validation Issues',
            'csrf_protection_gaps': '🛡️ CSRF Protection Issues',
            'file_security_gaps': '📁 File Security Issues',
            'logging_monitoring_gaps': '📊 Logging/Monitoring Gaps'
        }
        
        for key, title in categories.items():
            if key in results and results[key]:
                report.append(f"## {title}")
                report.append("")
                
                for gap in results[key][:10]:  # Limit to top 10 per category
                    report.append(f"### ⚠️ {gap['issue']}")
                    report.append(f"- **Severity**: {gap['severity']}")
                    report.append(f"- **File**: {gap['file']}")
                    if gap['line'] > 0:
                        report.append(f"- **Line**: {gap['line']}")
                    report.append(f"- **Code**: `{gap['code']}`")
                    report.append("")
                
                if len(results[key]) > 10:
                    report.append(f"... and {len(results[key]) - 10} more issues")
                    report.append("")
        
        # Security scores
        report.append("## 🎯 SECURITY SCORES BY COMPONENT")
        report.append("")
        scores = results['security_scores']
        for component, score in sorted(scores.items()):
            if component != 'overall':
                emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                report.append(f"- **{component.replace('_', ' ').title()}**: {emoji} {score:.1f}/100")
        report.append("")
        
        # Recommendations
        report.append("## 🔧 PRIORITY RECOMMENDATIONS")
        report.append("")
        
        if summary['critical_gaps'] > 0:
            report.append("### 🚨 IMMEDIATE ACTION REQUIRED:")
            report.append("1. Address all CRITICAL security issues immediately")
            report.append("2. Deploy patches for SQL injection vulnerabilities")
            report.append("3. Remove any hardcoded credentials")
            report.append("4. Disable dangerous functions (eval, exec)")
            report.append("")
        
        if summary['high_gaps'] > 0:
            report.append("### ⚠️ HIGH PRIORITY (Within 48 hours):")
            report.append("1. Add CSRF protection to unprotected endpoints")
            report.append("2. Implement proper authentication on sensitive endpoints")
            report.append("3. Add file upload security validation")
            report.append("4. Fix XSS vulnerabilities in templates")
            report.append("")
        
        report.append("### 📋 ONGOING IMPROVEMENTS:")
        report.append("1. Implement comprehensive security logging")
        report.append("2. Add security monitoring and alerting")
        report.append("3. Set up automated security testing")
        report.append("4. Regular security audits and penetration testing")
        report.append("")
        
        return "\n".join(report)


def main():
    """Main function to run security gap analysis."""
    analyzer = SecurityGapAnalyzer()
    results = analyzer.run_full_analysis()
    
    # Generate report
    report = analyzer.generate_report(results)
    
    # Save results
    with open('security_gap_analysis_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    with open('SECURITY_GAP_ANALYSIS_REPORT.md', 'w') as f:
        f.write(report)
    
    print("\n" + "="*60)
    print("🎉 SECURITY GAP ANALYSIS COMPLETED!")
    print("="*60)
    print(f"📊 Total gaps found: {results['summary']['total_gaps']}")
    print(f"🚨 Critical issues: {results['summary']['critical_gaps']}")
    print(f"⚠️  High priority issues: {results['summary']['high_gaps']}")
    print(f"🎯 Overall security score: {results['summary']['overall_score']:.1f}/100")
    print("\n📄 Reports generated:")
    print("- security_gap_analysis_results.json")
    print("- SECURITY_GAP_ANALYSIS_REPORT.md")
    print("- security_gap_analysis_diagrams.html")
    
    return results


if __name__ == "__main__":
    main()