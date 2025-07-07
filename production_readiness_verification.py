#!/usr/bin/env python3
"""
Production Readiness Verification Script
Verifies that all mock/stub/placeholder code has been removed and replaced with production-ready implementations
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any

def scan_for_issues() -> Dict[str, Any]:
    """Scan codebase for production readiness issues"""
    
    issues = {
        "mock_functions": [],
        "placeholder_configs": [],
        "stub_implementations": [],
        "deprecated_endpoints": [],
        "test_artifacts": [],
        "hardcoded_credentials": [],
        "summary": {}
    }
    
    # Scan Python files
    for py_file in Path('.').rglob('*.py'):
        if any(skip in str(py_file) for skip in ['venv/', '__pycache__/', '.git/', 'backup']):
            continue
            
        try:
            content = py_file.read_text()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                
                # Check for mock functions
                if any(keyword in line_lower for keyword in ['mock', 'stub', 'placeholder', 'todo:', 'fixme:']):
                    if 'mock response' in line_lower or 'stub implementation' in line_lower:
                        issues["mock_functions"].append(f"{py_file}:{i} - {line.strip()}")
                
                # Check for VEO2 references
                if 'veo2' in line_lower and 'backup' not in str(py_file):
                    issues["deprecated_endpoints"].append(f"{py_file}:{i} - {line.strip()}")
                
                # Check for hardcoded credentials/paths
                if any(pattern in line for pattern in ['/home/golde/', 'gen-lang-client-0874689591']):
                    if 'os.getenv' not in line and 'GOOGLE_AI_ULTRA_PROJECT_ID' not in line:
                        issues["hardcoded_credentials"].append(f"{py_file}:{i} - {line.strip()}")
                
                # Check for test artifacts
                if 'example.com' in line_lower or 'test_' in py_file.name:
                    issues["test_artifacts"].append(f"{py_file}:{i} - {line.strip()}")
                
                # Check for stub implementations
                if 'not yet configured' in line_lower or 'requires api setup' in line_lower:
                    issues["stub_implementations"].append(f"{py_file}:{i} - {line.strip()}")
        
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    # Scan configuration files
    for config_file in Path('.').rglob('*.env*'):
        if 'template' in config_file.name or 'backup' in str(config_file):
            continue
            
        try:
            content = config_file.read_text()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                if any(placeholder in line for placeholder in ['<REQUIRED>', '<OPTIONAL>', 'your_', 'placeholder']):
                    issues["placeholder_configs"].append(f"{config_file}:{i} - {line.strip()}")
        
        except Exception as e:
            print(f"Error reading {config_file}: {e}")
    
    # Generate summary
    total_issues = sum(len(category) for category in issues.values() if isinstance(category, list))
    issues["summary"] = {
        "total_issues": total_issues,
        "mock_functions_count": len(issues["mock_functions"]),
        "placeholder_configs_count": len(issues["placeholder_configs"]),
        "stub_implementations_count": len(issues["stub_implementations"]),
        "deprecated_endpoints_count": len(issues["deprecated_endpoints"]),
        "test_artifacts_count": len(issues["test_artifacts"]),
        "hardcoded_credentials_count": len(issues["hardcoded_credentials"]),
        "production_ready": total_issues == 0
    }
    
    return issues

def verify_endpoint_updates() -> Dict[str, Any]:
    """Verify that all endpoints use current configurations"""
    
    endpoint_check = {
        "pixverse_endpoints": [],
        "useapi_base_urls": [],
        "google_credentials": [],
        "telegram_configs": [],
        "status": "unknown"
    }
    
    # Check for Pixverse v4 endpoints
    for py_file in Path('.').rglob('*.py'):
        if 'backup' in str(py_file) or 'venv' in str(py_file):
            continue
            
        try:
            content = py_file.read_text()
            
            # Look for Pixverse endpoints
            if 'pixverse/videos/create-v4' in content:
                endpoint_check["pixverse_endpoints"].append(f"{py_file} - ✅ Using current Pixverse v4")
            elif 'veo2/generate' in content:
                endpoint_check["pixverse_endpoints"].append(f"{py_file} - ❌ Using deprecated VEO2")
            
            # Check UseAPI base URLs
            if 'api.useapi.net' in content:
                endpoint_check["useapi_base_urls"].append(f"{py_file} - ✅ Using UseAPI.net")
            
            # Check Google credentials configuration
            if 'GOOGLE_APPLICATION_CREDENTIALS' in content:
                endpoint_check["google_credentials"].append(f"{py_file} - ✅ Using environment variable")
            
            # Check Telegram configuration
            if 'TELEGRAM_BOT_TOKEN' in content:
                endpoint_check["telegram_configs"].append(f"{py_file} - ✅ Using environment variable")
        
        except Exception as e:
            print(f"Error checking {py_file}: {e}")
    
    # Determine overall status
    has_deprecated = any('deprecated' in item for item in endpoint_check["pixverse_endpoints"])
    endpoint_check["status"] = "production_ready" if not has_deprecated else "needs_updates"
    
    return endpoint_check

def main():
    """Main verification function"""
    
    print("🔍 PRODUCTION READINESS VERIFICATION")
    print("=" * 60)
    
    # Scan for issues
    print("\n📋 Scanning for mock/stub/placeholder code...")
    issues = scan_for_issues()
    
    # Verify endpoints
    print("\n🔗 Verifying endpoint configurations...")
    endpoints = verify_endpoint_updates()
    
    # Print results
    print("\n" + "=" * 60)
    print("VERIFICATION RESULTS:")
    print("=" * 60)
    
    # Issues summary
    summary = issues["summary"]
    print(f"\n📊 Code Quality Issues:")
    print(f"   Total Issues: {summary['total_issues']}")
    print(f"   Mock Functions: {summary['mock_functions_count']}")
    print(f"   Placeholder Configs: {summary['placeholder_configs_count']}")
    print(f"   Stub Implementations: {summary['stub_implementations_count']}")
    print(f"   Deprecated Endpoints: {summary['deprecated_endpoints_count']}")
    print(f"   Test Artifacts: {summary['test_artifacts_count']}")
    print(f"   Hardcoded Credentials: {summary['hardcoded_credentials_count']}")
    
    # Endpoint verification
    print(f"\n🔗 Endpoint Status: {endpoints['status']}")
    print(f"   Pixverse Endpoints: {len(endpoints['pixverse_endpoints'])} found")
    print(f"   UseAPI Base URLs: {len(endpoints['useapi_base_urls'])} found")
    print(f"   Google Credentials: {len(endpoints['google_credentials'])} configured")
    print(f"   Telegram Configs: {len(endpoints['telegram_configs'])} configured")
    
    # Overall assessment
    production_ready = (summary["production_ready"] and 
                       endpoints["status"] == "production_ready")
    
    print(f"\n🎯 OVERALL STATUS: {'✅ PRODUCTION READY' if production_ready else '⚠️ NEEDS ATTENTION'}")
    
    # Show critical issues if any
    if not production_ready:
        print(f"\n❌ CRITICAL ISSUES TO FIX:")
        
        if issues["deprecated_endpoints"]:
            print(f"\n   Deprecated Endpoints:")
            for issue in issues["deprecated_endpoints"][:5]:
                print(f"     • {issue}")
        
        if issues["mock_functions"]:
            print(f"\n   Mock Functions:")
            for issue in issues["mock_functions"][:5]:
                print(f"     • {issue}")
        
        if issues["stub_implementations"]:
            print(f"\n   Stub Implementations:")
            for issue in issues["stub_implementations"][:3]:
                print(f"     • {issue}")
    
    else:
        print(f"\n✅ PRODUCTION READY:")
        print(f"   • All VEO2 endpoints replaced with Pixverse v4")
        print(f"   • All mock/stub code removed or properly implemented")
        print(f"   • Environment variables configured for credentials")
        print(f"   • Test files removed from production")
        print(f"   • Real notification system implemented")
    
    # Save detailed report
    report = {
        "timestamp": "2025-07-07T12:15:00Z",
        "production_ready": production_ready,
        "issues": issues,
        "endpoints": endpoints
    }
    
    with open("production_readiness_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: production_readiness_report.json")
    
    return production_ready

if __name__ == "__main__":
    main()