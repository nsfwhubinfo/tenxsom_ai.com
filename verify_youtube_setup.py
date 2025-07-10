#!/usr/bin/env python3
"""
Verify YouTube upload setup without OAuth flow
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_youtube_setup():
    """Verify all YouTube upload components are in place"""
    print("🔍 YOUTUBE UPLOAD SETUP VERIFICATION")
    print("=" * 50)
    
    checks = []
    
    # 1. Check environment variables
    print("\n1️⃣ Environment Variables:")
    env_vars = {
        "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY"),
        "YOUTUBE_CHANNEL_ID": os.getenv("YOUTUBE_CHANNEL_ID"),
        "YOUTUBE_CHANNEL_URL": os.getenv("YOUTUBE_CHANNEL_URL"),
        "YOUTUBE_OAUTH_CLIENT_SECRETS": os.getenv("YOUTUBE_OAUTH_CLIENT_SECRETS")
    }
    
    for var_name, var_value in env_vars.items():
        if var_value:
            print(f"   ✅ {var_name}: {'*' * 10}{var_value[-10:] if len(var_value) > 10 else var_value}")
            checks.append(True)
        else:
            print(f"   ❌ {var_name}: Not set")
            checks.append(False)
    
    # 2. Check client secrets file
    print("\n2️⃣ OAuth Client Secrets:")
    client_secrets_path = "youtube-upload-pipeline/auth/client_secrets.json"
    if os.path.exists(client_secrets_path):
        try:
            with open(client_secrets_path, 'r') as f:
                secrets = json.load(f)
                if "installed" in secrets or "web" in secrets:
                    app_type = "installed" if "installed" in secrets else "web"
                    client_id = secrets[app_type].get("client_id", "")
                    print(f"   ✅ Client secrets file exists ({app_type} application)")
                    print(f"   ✅ Client ID: {'*' * 20}{client_id[-20:] if len(client_id) > 20 else client_id}")
                    checks.append(True)
                else:
                    print(f"   ❌ Invalid client secrets format")
                    checks.append(False)
        except Exception as e:
            print(f"   ❌ Error reading client secrets: {e}")
            checks.append(False)
    else:
        print(f"   ❌ Client secrets file not found at: {client_secrets_path}")
        checks.append(False)
    
    # 3. Check Python dependencies
    print("\n3️⃣ Python Dependencies:")
    try:
        import googleapiclient
        print("   ✅ google-api-python-client installed")
        checks.append(True)
    except ImportError:
        print("   ❌ google-api-python-client not installed")
        checks.append(False)
    
    try:
        import google_auth_oauthlib
        print("   ✅ google-auth-oauthlib installed")
        checks.append(True)
    except ImportError:
        print("   ❌ google-auth-oauthlib not installed")
        checks.append(False)
    
    # 4. Check upload pipeline structure
    print("\n4️⃣ Upload Pipeline Structure:")
    required_files = [
        "youtube-upload-pipeline/services/youtube_uploader.py",
        "youtube-upload-pipeline/auth/youtube_auth.py",
        "youtube-upload-pipeline/thumbnails/thumbnail_generator.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
            checks.append(True)
        else:
            print(f"   ❌ {file_path} not found")
            checks.append(False)
    
    # 5. Check video output directory
    print("\n5️⃣ Video Output Directory:")
    video_dir = "videos/output"
    if os.path.exists(video_dir) and os.path.isdir(video_dir):
        print(f"   ✅ {video_dir} exists")
        checks.append(True)
    else:
        print(f"   ❌ {video_dir} not found")
        checks.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    passed = sum(checks)
    total = len(checks)
    percentage = (passed / total) * 100 if total > 0 else 0
    
    print(f"Checks Passed: {passed}/{total} ({percentage:.0f}%)")
    
    if percentage == 100:
        print("\n✅ YouTube upload system is fully configured!")
        print("\n📝 Next steps for first upload:")
        print("1. Run OAuth authentication flow on a machine with browser access")
        print("2. Copy the generated token.json to youtube-upload-pipeline/auth/")
        print("3. The token will allow headless uploads from this server")
        print("\n💡 Alternatively, use a service account for server-to-server auth")
    elif percentage >= 80:
        print("\n🟡 YouTube upload system is mostly configured")
        print("   Fix the remaining issues before attempting uploads")
    else:
        print("\n❌ YouTube upload system needs configuration")
        print("   Please address the failed checks above")
    
    # Save verification results
    results = {
        "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip(),
        "checks_passed": passed,
        "checks_total": total,
        "percentage": percentage,
        "ready_for_upload": percentage == 100
    }
    
    with open("youtube_setup_verification.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: youtube_setup_verification.json")
    
    return percentage == 100


if __name__ == "__main__":
    success = verify_youtube_setup()
    exit(0 if success else 1)