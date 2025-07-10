#!/usr/bin/env python3
"""
Prepare and execute live video upload to YouTube channel
Final production readiness check
"""

import asyncio
import os
import json
import sys
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()

class LiveUploadPreparation:
    """Prepare system for live upload"""
    
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "checks": [],
            "ready_for_upload": False
        }
    
    async def check_mcp_integration(self) -> bool:
        """Check MCP server integration"""
        print("🔧 Checking MCP Integration...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get a real template
                response = await client.get(f"{self.mcp_server_url}/api/templates?limit=1")
                if response.status_code != 200:
                    raise Exception(f"MCP templates failed: {response.status_code}")
                
                templates = response.json().get("templates", [])
                if not templates:
                    raise Exception("No templates available")
                
                template_name = templates[0]["template_name"]
                print(f"   ✅ Found template: {template_name}")
                
                # Test template processing
                process_payload = {
                    "template_name": template_name,
                    "context_variables": {
                        "target_audience": "AI enthusiasts",
                        "current_trends": ["artificial intelligence", "automation", "future tech"],
                        "duration_preference": "short",
                        "content_style": "educational",
                        "platform_focus": "youtube"
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
                    raise Exception(f"Template error: {result['error']}")
                
                print(f"   ✅ Template processing successful")
                return True
                
        except Exception as e:
            print(f"   ❌ MCP Integration failed: {e}")
            return False
    
    async def check_useapi_connection(self) -> bool:
        """Verify UseAPI.net is ready for production"""
        print("\n🔗 Checking UseAPI.net Connection...")
        
        token = os.getenv("USEAPI_BEARER_TOKEN")
        if not token:
            print("   ❌ No UseAPI bearer token")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {token}"}
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Test with Pixverse endpoint (confirmed working)
                response = await client.get(
                    "https://api.useapi.net/v2/pixverse/videos",
                    headers=headers
                )
                
                # 200, 400, or 404 indicate auth is working (400 = needs config, but auth valid)
                if response.status_code in [200, 400, 404]:
                    status_msg = "working" if response.status_code == 200 else "authenticated (needs service config)"
                    print(f"   ✅ UseAPI.net {status_msg}")
                    return True
                else:
                    print(f"   ❌ UseAPI.net returned {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"   ❌ UseAPI.net error: {e}")
            return False
    
    def check_production_config(self) -> bool:
        """Check production configuration"""
        print("\n⚙️ Checking Production Configuration...")
        
        required_vars = [
            "YOUTUBE_API_KEY",
            "YOUTUBE_CHANNEL_ID", 
            "USEAPI_BEARER_TOKEN",
            "CLOUD_TASKS_WORKER_URL",
            "MCP_SERVER_URL"
        ]
        
        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)
        
        if missing:
            print(f"   ❌ Missing variables: {', '.join(missing)}")
            return False
        
        # Check environment is set to production
        env = os.getenv("ENVIRONMENT", "development")
        debug = os.getenv("DEBUG_MODE", "true").lower()
        
        if env != "production":
            print(f"   ⚠️  Environment is '{env}', should be 'production'")
        
        if debug == "true":
            print(f"   ⚠️  Debug mode is enabled")
        
        print("   ✅ All required environment variables present")
        return True
    
    def check_file_structure(self) -> bool:
        """Check production file structure"""
        print("\n📁 Checking File Structure...")
        
        required_paths = [
            "videos/output",
            "monitoring/alerts", 
            "flow_reports",
            "youtube-upload-pipeline/auth/client_secrets.json",
            "tenxsom_flow_engine/run_flow.py"
        ]
        
        missing = []
        for path in required_paths:
            if not os.path.exists(path):
                missing.append(path)
        
        if missing:
            print(f"   ❌ Missing paths: {', '.join(missing)}")
            return False
        
        print("   ✅ All required paths exist")
        return True
    
    async def generate_test_video_metadata(self) -> dict:
        """Generate metadata for test video using MCP"""
        print("\n🎬 Generating Test Video Metadata...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get an educational template
                response = await client.get(f"{self.mcp_server_url}/api/templates")
                templates = response.json().get("templates", [])
                
                # Find a suitable template
                selected_template = None
                for template in templates:
                    if "educational" in template.get("description", "").lower() or \
                       "tech" in template.get("template_name", "").lower():
                        selected_template = template
                        break
                
                if not selected_template:
                    selected_template = templates[0]  # Use first available
                
                # Generate production-ready metadata
                context = {
                    "target_audience": "AI and technology enthusiasts",
                    "current_trends": ["artificial intelligence", "machine learning", "automation"],
                    "duration_preference": "short",
                    "content_style": "educational",
                    "platform_focus": "youtube",
                    "urgency": "high",
                    "brand_voice": "professional yet accessible"
                }
                
                response = await client.post(
                    f"{self.mcp_server_url}/api/templates/process",
                    json={
                        "template_name": selected_template["template_name"],
                        "context_variables": context
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Generated metadata using template: {selected_template['template_name']}")
                    return {
                        "template_used": selected_template["template_name"],
                        "metadata": result,
                        "context": context
                    }
                else:
                    raise Exception(f"Failed to generate metadata: {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ Metadata generation failed: {e}")
            # Fallback metadata
            return {
                "template_used": "fallback",
                "metadata": {
                    "title": f"TenxsomAI Test Upload - {datetime.now().strftime('%Y-%m-%d')}",
                    "description": "This is a test upload from the TenxsomAI automated system.",
                    "tags": ["AI", "automation", "technology", "test"]
                },
                "context": {}
            }
    
    async def run_pre_upload_checks(self):
        """Run all pre-upload checks"""
        print("🚀 LIVE UPLOAD PREPARATION")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print("=" * 50)
        
        checks = [
            ("MCP Integration", await self.check_mcp_integration()),
            ("UseAPI Connection", await self.check_useapi_connection()),
            ("Production Config", self.check_production_config()),
            ("File Structure", self.check_file_structure())
        ]
        
        # Record results
        for check_name, result in checks:
            self.results["checks"].append({
                "name": check_name,
                "passed": result
            })
        
        # Generate test metadata
        test_metadata = await self.generate_test_video_metadata()
        self.results["test_metadata"] = test_metadata
        
        # Summary
        passed = sum(1 for _, result in checks if result)
        total = len(checks)
        
        print(f"\n📊 READINESS SUMMARY")
        print("=" * 30)
        
        for check_name, result in checks:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{check_name}: {status}")
        
        print(f"\nOverall: {passed}/{total} checks passed")
        
        self.results["ready_for_upload"] = (passed == total)
        
        if self.results["ready_for_upload"]:
            print("\n🎉 SYSTEM READY FOR LIVE UPLOAD!")
            print(f"📝 Test video metadata generated using: {test_metadata['template_used']}")
            print("\nNext steps:")
            print("1. Create/select a video file for upload")
            print("2. Run the live upload with generated metadata")
            print("3. Monitor upload progress and success")
        else:
            print("\n⚠️ SYSTEM NOT READY - Fix failed checks before proceeding")
        
        # Save results
        with open("live_upload_readiness.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Results saved to: live_upload_readiness.json")
        
        return self.results["ready_for_upload"]


async def main():
    """Main preparation function"""
    prep = LiveUploadPreparation()
    ready = await prep.run_pre_upload_checks()
    
    if ready:
        print("\n🚀 Ready to proceed with live upload!")
        sys.exit(0)
    else:
        print("\n❌ Not ready for live upload")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())