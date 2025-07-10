#!/usr/bin/env python3
"""
Prepare Hub Channel OAuth Instructions
Since we're in a headless environment, this provides clear steps
"""

import os
import json
from datetime import datetime
from pathlib import Path

def check_existing_auth():
    """Check for existing authentication"""
    print("🔍 Checking existing authentication...")
    
    # Check for existing tokens
    token_locations = [
        "youtube-upload-pipeline/auth/token.json",
        "youtube-upload-pipeline/auth/channel_tokens/token_hub.json"
    ]
    
    for token_path in token_locations:
        if os.path.exists(token_path):
            print(f"✅ Found existing token: {token_path}")
            
            try:
                with open(token_path, 'r') as f:
                    token_data = json.load(f)
                    
                # Check if it has refresh token
                if token_data.get("refresh_token"):
                    print("   ✅ Contains refresh token")
                    return token_path, True
                else:
                    print("   ❌ Missing refresh token")
            except:
                print("   ❌ Invalid token file")
    
    return None, False

def generate_oauth_instructions():
    """Generate instructions for OAuth flow"""
    print("\n📋 HUB CHANNEL OAUTH INSTRUCTIONS")
    print("=" * 50)
    
    instructions = {
        "option_a_local_machine": {
            "description": "Run OAuth on machine with browser",
            "steps": [
                "1. Copy these files to a machine with browser access:",
                "   - youtube-upload-pipeline/auth/client_secrets.json",
                "   - multi_channel_oauth_flow.py",
                "2. Install dependencies:",
                "   pip install google-auth-oauthlib google-auth-httplib2",
                "3. Run OAuth flow:",
                "   python3 multi_channel_oauth_flow.py",
                "4. Select option 1 (hub channel)",
                "5. Complete browser authentication",
                "6. Copy generated token file back to server:",
                "   - youtube-upload-pipeline/auth/channel_tokens/token_hub.json"
            ]
        },
        "option_b_cloud_shell": {
            "description": "Use Google Cloud Shell (has browser)",
            "steps": [
                "1. Open Google Cloud Console",
                "2. Click 'Activate Cloud Shell' button",
                "3. Upload client_secrets.json to Cloud Shell",
                "4. Run OAuth flow in Cloud Shell",
                "5. Download token file and upload to server"
            ]
        },
        "option_c_ssh_tunnel": {
            "description": "SSH tunnel for remote OAuth",
            "steps": [
                "1. SSH to server with port forwarding:",
                "   ssh -L 8080:localhost:8080 user@server",
                "2. Run OAuth flow on server",
                "3. Open browser on local machine to displayed URL",
                "4. Complete authentication"
            ]
        }
    }
    
    print("\n🔐 Since we're in a headless environment, use one of these methods:\n")
    
    for option_key, option in instructions.items():
        print(f"\n{option_key.upper().replace('_', ' ')}:")
        print(f"Description: {option['description']}")
        print("Steps:")
        for step in option['steps']:
            print(f"   {step}")
    
    # Save instructions
    with open("hub_oauth_instructions.json", "w") as f:
        json.dump(instructions, f, indent=2)
    
    print(f"\n💾 Instructions saved to: hub_oauth_instructions.json")
    
    return instructions

def create_quick_test_script():
    """Create script to test YouTube connection after OAuth"""
    test_script = '''#!/usr/bin/env python3
"""
Quick test of YouTube OAuth authentication
"""

import sys
sys.path.append("youtube-upload-pipeline")

from services.multi_channel_token_manager import get_token_manager

def test_hub_channel():
    """Test hub channel authentication"""
    try:
        manager = get_token_manager()
        
        # Check channel status
        channels = manager.list_available_channels()
        print("\\n📺 Channel Status:")
        for key, info in channels.items():
            status = "✅" if info["ready"] else "❌"
            print(f"   {status} {info['name']} ({info['role']})")
        
        # Test hub channel
        if channels["hub"]["ready"]:
            print("\\n🔐 Testing hub channel connection...")
            youtube, channel_info = manager.get_channel_service("hub")
            
            # Get channel details
            response = youtube.channels().list(
                part="snippet,statistics",
                mine=True
            ).execute()
            
            if response["items"]:
                channel = response["items"][0]
                print(f"\\n✅ Connected to: {channel['snippet']['title']}")
                print(f"   Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}")
                print(f"   Total videos: {channel['statistics'].get('videoCount', '0')}")
                print(f"   Total views: {channel['statistics'].get('viewCount', '0')}")
                
                return True
        else:
            print("\\n❌ Hub channel not authenticated yet")
            return False
            
    except Exception as e:
        print(f"\\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_hub_channel()
    sys.exit(0 if success else 1)
'''
    
    with open("test_youtube_connection.py", "w") as f:
        f.write(test_script)
    
    os.chmod("test_youtube_connection.py", 0o755)
    print("\n✅ Created test script: test_youtube_connection.py")

def main():
    """Main preparation function"""
    print("🎬 PREPARING HUB CHANNEL OAUTH")
    print("=" * 50)
    
    # Check existing auth
    existing_token, has_refresh = check_existing_auth()
    
    if existing_token and has_refresh:
        print("\n✅ EXISTING AUTHENTICATION FOUND!")
        print(f"   Token location: {existing_token}")
        print("\n🎉 You may already be authenticated!")
        print("\n🧪 Test the connection with:")
        print("   python3 test_youtube_connection.py")
    else:
        print("\n❌ No valid authentication found")
        
        # Generate instructions
        generate_oauth_instructions()
        
        print("\n⚠️  IMPORTANT: Hub channel OAuth requires browser")
        print("   This is a one-time setup per channel")
        print("   The refresh token will allow headless uploads")
    
    # Create test script
    create_quick_test_script()
    
    print("\n📋 SUMMARY:")
    print("=" * 30)
    
    if existing_token and has_refresh:
        print("Status: POSSIBLY READY")
        print("Next step: Run test_youtube_connection.py")
    else:
        print("Status: OAUTH NEEDED")
        print("Next step: Complete OAuth using one of the methods above")
    
    print("\n🚀 After OAuth is complete:")
    print("1. Test connection: python3 test_youtube_connection.py")
    print("2. Execute live upload: python3 execute_live_upload.py")
    print("3. Set up spoke channels incrementally")

if __name__ == "__main__":
    main()