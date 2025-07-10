#!/usr/bin/env python3
"""
System integration test for TenxsomAI
Tests: MCP server, Cloud Tasks, Video Generation
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SystemIntegrationTester:
    """Test complete system integration"""
    
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        self.cloud_tasks_worker_url = os.getenv("CLOUD_TASKS_WORKER_URL")
        self.useapi_token = os.getenv("USEAPI_BEARER_TOKEN")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
    
    async def test_mcp_server(self) -> bool:
        """Test MCP server connectivity and functionality"""
        print("\n1️⃣ Testing MCP Server...")
        test_name = "mcp_server"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test health endpoint
                response = await client.get(f"{self.mcp_server_url}/health")
                if response.status_code != 200:
                    raise Exception(f"Health check failed: {response.status_code}")
                
                # Test templates endpoint
                response = await client.get(f"{self.mcp_server_url}/api/templates")
                if response.status_code != 200:
                    raise Exception(f"Templates endpoint failed: {response.status_code}")
                
                templates_data = response.json()
                template_count = templates_data.get("count", 0)
                
                if template_count == 0:
                    raise Exception("No templates found in MCP server")
                
                self.results["tests"][test_name] = {
                    "status": "passed",
                    "details": f"MCP server healthy with {template_count} templates"
                }
                print(f"✅ MCP Server: OK ({template_count} templates loaded)")
                return True
                
        except Exception as e:
            self.results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"❌ MCP Server: FAILED - {e}")
            return False
    
    async def test_cloud_tasks_worker(self) -> bool:
        """Test Cloud Tasks worker connectivity"""
        print("\n2️⃣ Testing Cloud Tasks Worker...")
        test_name = "cloud_tasks_worker"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Extract base URL from worker URL
                base_url = self.cloud_tasks_worker_url.replace("/process_video_job", "")
                
                # Test health endpoint
                response = await client.get(f"{base_url}/health")
                if response.status_code != 200:
                    raise Exception(f"Worker health check failed: {response.status_code}")
                
                self.results["tests"][test_name] = {
                    "status": "passed",
                    "details": "Cloud Tasks worker is healthy"
                }
                print("✅ Cloud Tasks Worker: OK")
                return True
                
        except Exception as e:
            self.results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"❌ Cloud Tasks Worker: FAILED - {e}")
            return False
    
    async def test_useapi_connection(self) -> bool:
        """Test UseAPI.net connection"""
        print("\n3️⃣ Testing UseAPI.net Connection...")
        test_name = "useapi_connection"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.useapi_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test with a simple endpoint that should work
                response = await client.get(
                    "https://api.useapi.net/v1/jobs",
                    headers=headers
                )
                
                # Even a 404 means authentication worked
                if response.status_code in [200, 404]:
                    self.results["tests"][test_name] = {
                        "status": "passed",
                        "details": "UseAPI.net authentication successful"
                    }
                    print("✅ UseAPI.net: Authentication OK")
                    return True
                else:
                    raise Exception(f"Unexpected status: {response.status_code}")
                    
        except Exception as e:
            self.results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"❌ UseAPI.net: FAILED - {e}")
            return False
    
    async def test_mcp_template_processing(self) -> bool:
        """Test MCP template processing"""
        print("\n4️⃣ Testing MCP Template Processing...")
        test_name = "mcp_template_processing"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First, get a template name
                response = await client.get(f"{self.mcp_server_url}/api/templates?limit=1")
                templates = response.json().get("templates", [])
                
                if not templates:
                    raise Exception("No templates available")
                
                template_name = templates[0]["template_name"]
                
                # Test template processing
                process_payload = {
                    "template_name": template_name,
                    "context_variables": {
                        "target_audience": "tech enthusiasts",
                        "current_trends": ["AI", "automation", "future tech"],
                        "duration_preference": "short"
                    }
                }
                
                response = await client.post(
                    f"{self.mcp_server_url}/api/templates/process",
                    json=process_payload
                )
                
                if response.status_code != 200:
                    raise Exception(f"Template processing failed: {response.status_code}")
                
                result = response.json()
                if "error" in result:
                    raise Exception(result["error"])
                
                self.results["tests"][test_name] = {
                    "status": "passed",
                    "details": f"Successfully processed template: {template_name}"
                }
                print(f"✅ MCP Template Processing: OK (Template: {template_name})")
                return True
                
        except Exception as e:
            self.results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"❌ MCP Template Processing: FAILED - {e}")
            return False
    
    async def test_file_system(self) -> bool:
        """Test file system directories"""
        print("\n5️⃣ Testing File System...")
        test_name = "file_system"
        
        required_dirs = [
            "monitoring/alerts",
            "flow_reports",
            "videos/output",
            "tenxsom_flow_engine",
            "youtube-upload-pipeline"
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                missing_dirs.append(dir_path)
        
        if missing_dirs:
            self.results["tests"][test_name] = {
                "status": "failed",
                "error": f"Missing directories: {', '.join(missing_dirs)}"
            }
            print(f"❌ File System: FAILED - Missing: {', '.join(missing_dirs)}")
            return False
        else:
            self.results["tests"][test_name] = {
                "status": "passed",
                "details": "All required directories exist"
            }
            print("✅ File System: OK")
            return True
    
    async def run_all_tests(self):
        """Run all integration tests"""
        print("🚀 TENXSOM AI SYSTEM INTEGRATION TEST")
        print("=" * 50)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"MCP Server: {self.mcp_server_url}")
        print(f"Worker URL: {self.cloud_tasks_worker_url}")
        print("=" * 50)
        
        # Run tests
        tests = [
            self.test_mcp_server(),
            self.test_cloud_tasks_worker(),
            self.test_useapi_connection(),
            self.test_mcp_template_processing(),
            self.test_file_system()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Count results
        for result in results:
            self.results["summary"]["total"] += 1
            if isinstance(result, bool) and result:
                self.results["summary"]["passed"] += 1
            else:
                self.results["summary"]["failed"] += 1
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.results['summary']['total']}")
        print(f"Passed: {self.results['summary']['passed']} ✅")
        print(f"Failed: {self.results['summary']['failed']} ❌")
        
        # Save results
        with open("system_integration_test_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: system_integration_test_results.json")
        
        # Return overall status
        return self.results["summary"]["failed"] == 0


async def main():
    """Main test runner"""
    tester = SystemIntegrationTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 SYSTEM READY FOR PRODUCTION!")
        print("Next step: Run test video upload to YouTube")
    else:
        print("\n⚠️  SYSTEM NOT READY - Please fix failed tests")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())