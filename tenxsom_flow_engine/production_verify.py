#!/usr/bin/env python3

"""
Production Deployment Verification
Verifies the Flow Engine is ready for production deployment
"""

import os
import sys
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_redis_setup():
    """Verify Redis is configured for job queue"""
    try:
        # Check if Redis is available in requirements
        req_file = Path(__file__).parent / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                content = f.read()
                if "redis" in content:
                    logger.info("✅ Redis configured in requirements")
                    return True
        logger.error("❌ Redis not found in requirements")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to verify Redis setup: {e}")
        return False

def verify_credentials():
    """Verify Google AI Ultra credentials file exists"""
    creds_path = "/home/golde/.google-ai-ultra-credentials.json"
    try:
        if os.path.exists(creds_path):
            with open(creds_path, 'r') as f:
                creds = json.load(f)
                if "project_id" in creds:
                    logger.info("✅ Credentials file exists and is valid JSON")
                    logger.info(f"📝 Note: Update credentials for production project gen-lang-client-0874689591")
                    return True
                else:
                    logger.error("❌ Invalid credentials format")
                    return False
        else:
            logger.error(f"❌ Credentials file not found: {creds_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to verify credentials: {e}")
        return False

def verify_no_test_artifacts():
    """Verify no test artifacts remain"""
    base_path = Path(__file__).parent.parent
    
    # Check for test files
    test_files = list(base_path.glob("**/test_*.py"))
    test_files.extend(list(base_path.glob("**/*test*.py")))
    
    # Filter out virtual environment files
    test_files = [f for f in test_files if 'venv' not in str(f) and 'tenxsom-env' not in str(f)]
    
    if test_files:
        logger.error(f"❌ Test files found: {[str(f) for f in test_files]}")
        return False
    else:
        logger.info("✅ No test artifacts found")
        return True

def verify_production_config():
    """Verify all configurations are production-ready"""
    config_file = Path(__file__).parent / "tools" / "veo_tool_functions.py"
    
    try:
        with open(config_file, 'r') as f:
            content = f.read()
            if "gen-lang-client-0874689591" in content:
                logger.info("✅ Production project ID configured")
                return True
            else:
                logger.error("❌ Incorrect project ID in configuration")
                return False
    except Exception as e:
        logger.error(f"❌ Failed to verify configuration: {e}")
        return False

def verify_systemd_service():
    """Verify systemd service file exists"""
    service_file = Path(__file__).parent / "tenxsom-flow-worker.service"
    
    if service_file.exists():
        logger.info("✅ SystemD service file exists")
        return True
    else:
        logger.error("❌ SystemD service file missing")
        return False

def main():
    """Run all production verification checks"""
    logger.info("🔍 TENXSOM AI PRODUCTION VERIFICATION")
    logger.info("=" * 60)
    
    checks = [
        ("Redis Setup", verify_redis_setup),
        ("Google AI Ultra Credentials", verify_credentials),
        ("No Test Artifacts", verify_no_test_artifacts),
        ("Production Configuration", verify_production_config),
        ("SystemD Service File", verify_systemd_service)
    ]
    
    results = []
    for check_name, check_func in checks:
        logger.info(f"\n🔧 Running check: {check_name}")
        result = check_func()
        results.append((check_name, result))
    
    # Summary
    logger.info("\n📋 VERIFICATION SUMMARY")
    logger.info("-" * 40)
    
    passed = 0
    for check_name, result in results:
        status = "PASS" if result else "FAIL"
        emoji = "✅" if result else "❌"
        logger.info(f"{emoji} {check_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    logger.info(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        logger.info("🎉 ALL CHECKS PASSED - READY FOR PRODUCTION!")
        return True
    else:
        logger.error("💥 SOME CHECKS FAILED - NOT READY FOR PRODUCTION")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)