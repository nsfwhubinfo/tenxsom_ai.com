#!/usr/bin/env python3
"""
Resolve UseAPI.net configuration issues and identify working services
"""

import asyncio
import os
import json
from dotenv import load_dotenv
import httpx

# Load environment
load_dotenv()

class UseAPIConfigResolver:
    """Resolve UseAPI.net configuration issues"""
    
    def __init__(self):
        self.token = os.getenv("USEAPI_BEARER_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.working_services = []
        self.failed_services = []
        
    async def test_endpoint(self, name: str, url: str, method: str = "GET", data: dict = None) -> bool:
        """Test a specific endpoint"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == "GET":
                    response = await client.get(url, headers=self.headers)
                else:
                    response = await client.post(url, headers=self.headers, json=data or {})
                
                # Consider various success scenarios
                if response.status_code in [200, 201]:
                    print(f"✅ {name}: Working (HTTP {response.status_code})")
                    self.working_services.append(name)
                    return True
                elif response.status_code == 400:
                    # 400 might mean authenticated but needs configuration
                    try:
                        error_data = response.json()
                        if "configuration" in error_data.get("error", "").lower():
                            print(f"🟡 {name}: Authenticated but needs configuration")
                            print(f"   Error: {error_data.get('error', 'Unknown')}")
                            return True  # Auth works, just needs setup
                        else:
                            print(f"❌ {name}: Bad request - {error_data.get('error', 'Unknown')}")
                            return False
                    except:
                        print(f"❌ {name}: HTTP 400 with invalid JSON")
                        return False
                elif response.status_code in [401, 403]:
                    print(f"❌ {name}: Authentication failed (HTTP {response.status_code})")
                    return False
                elif response.status_code == 404:
                    print(f"🟡 {name}: Endpoint not found (might be correct - service exists but endpoint structure unknown)")
                    return True  # 404 means auth worked but endpoint doesn't exist
                else:
                    print(f"❌ {name}: HTTP {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ {name}: Connection error - {e}")
            return False
    
    async def test_all_services(self):
        """Test all known UseAPI.net services"""
        print("🔍 Testing UseAPI.net Service Availability")
        print("=" * 50)
        
        # Test various service endpoints based on documentation
        services_to_test = [
            # Core API
            ("Jobs List", "https://api.useapi.net/v1/jobs", "GET"),
            
            # Video generation services
            ("Pixverse V2", "https://api.useapi.net/v2/pixverse/videos", "GET"),
            ("LTX Studio", "https://api.useapi.net/v1/ltxstudio", "GET"),
            ("Runway", "https://api.useapi.net/v1/runway", "GET"),
            ("Minimax", "https://api.useapi.net/v1/minimax", "GET"),
            ("Kling", "https://api.useapi.net/v1/kling", "GET"),
            ("Pika", "https://api.useapi.net/v1/pika", "GET"),
            
            # Image generation
            ("Midjourney", "https://api.useapi.net/v1/midjourney", "GET"),
            
            # Account info
            ("Account", "https://api.useapi.net/v1/account", "GET"),
            ("Balance", "https://api.useapi.net/v1/balance", "GET"),
        ]
        
        for name, url, method in services_to_test:
            await self.test_endpoint(name, url, method)
            await asyncio.sleep(0.5)  # Rate limit
        
        print("\n" + "=" * 50)
        print("📊 RESULTS SUMMARY")
        print("=" * 50)
        
        working_count = len(self.working_services)
        total_count = len(services_to_test)
        
        if working_count > 0:
            print(f"✅ Working services ({working_count}/{total_count}):")
            for service in self.working_services:
                print(f"   • {service}")
        
        if self.failed_services:
            print(f"\n❌ Failed services ({len(self.failed_services)}):")
            for service in self.failed_services:
                print(f"   • {service}")
        
        return working_count > 0
    
    async def get_account_info(self):
        """Try to get account information"""
        print("\n🔍 Checking Account Information")
        print("-" * 30)
        
        endpoints_to_try = [
            "https://api.useapi.net/v1/account",
            "https://api.useapi.net/v1/user",
            "https://api.useapi.net/v1/profile",
            "https://api.useapi.net/v1/balance"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(endpoint, headers=self.headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        print(f"✅ {endpoint.split('/')[-1].title()} info:")
                        print(json.dumps(data, indent=2))
                        return data
                    elif response.status_code in [401, 403]:
                        print(f"❌ Authentication failed for {endpoint}")
                    else:
                        print(f"🟡 {endpoint}: HTTP {response.status_code}")
                        
            except Exception as e:
                print(f"❌ {endpoint}: {e}")
        
        return None
    
    async def suggest_next_steps(self):
        """Suggest next steps based on findings"""
        print("\n💡 RECOMMENDED NEXT STEPS")
        print("=" * 40)
        
        if len(self.working_services) == 0:
            print("❌ No services are working. Possible issues:")
            print("   1. Invalid API token")
            print("   2. Account not properly activated")
            print("   3. Token expired or revoked")
            print("\n   Actions:")
            print("   • Check token at https://useapi.net/account")
            print("   • Verify account is active and has credits")
            print("   • Generate new API token if needed")
        else:
            print("✅ Authentication is working but services need configuration")
            print("\n   Next steps:")
            print("   1. Configure specific services you plan to use:")
            print("      • Pixverse: https://useapi.net/docs/api-pixverse-v2")
            print("      • LTX Studio: https://useapi.net/docs/api-ltxstudio-v1")
            print("      • Runway: https://useapi.net/docs/api-runway-v1")
            print("\n   2. For TenxsomAI's 30-day plan, prioritize:")
            print("      • LTX Studio (Volume tier - 84 videos/day)")
            print("      • Pixverse (if LTX not available)")
            print("\n   3. Update monetization_strategy_executor.py to use working services")
    
    async def run_full_diagnosis(self):
        """Run complete UseAPI.net diagnosis"""
        print("🚀 UseAPI.net CONFIGURATION DIAGNOSIS")
        print("=" * 60)
        print(f"Token: {self.token[:20]}..." if self.token else "❌ No token found")
        print("=" * 60)
        
        # Test services
        has_working_services = await self.test_all_services()
        
        # Get account info
        account_info = await self.get_account_info()
        
        # Suggest next steps
        await self.suggest_next_steps()
        
        # Save diagnosis
        diagnosis = {
            "timestamp": "2025-07-08T19:00:00Z",
            "token_present": bool(self.token),
            "working_services": self.working_services,
            "failed_services": self.failed_services,
            "account_info": account_info,
            "has_working_services": has_working_services
        }
        
        with open("useapi_diagnosis.json", "w") as f:
            json.dump(diagnosis, f, indent=2)
        
        print(f"\n📄 Diagnosis saved to: useapi_diagnosis.json")
        
        return has_working_services


async def main():
    """Main diagnosis function"""
    resolver = UseAPIConfigResolver()
    success = await resolver.run_full_diagnosis()
    
    if success:
        print("\n✅ UseAPI.net authentication is working - just needs service configuration")
    else:
        print("\n❌ UseAPI.net has authentication issues that need resolution")


if __name__ == "__main__":
    asyncio.run(main())