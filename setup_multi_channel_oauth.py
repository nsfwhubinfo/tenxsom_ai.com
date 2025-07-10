#!/usr/bin/env python3
"""
Setup Multi-Channel OAuth Application
Step 1: Create single OAuth2 application for all TenxsomAI channels
"""

import os
import json
import sys
from datetime import datetime
from pathlib import Path

class MultiChannelOAuthSetup:
    """Setup OAuth for multi-channel YouTube management"""
    
    def __init__(self):
        self.setup_log = []
        self.oauth_config = {
            "application_name": "TenxsomAI Multi-Channel Manager",
            "channels": {
                "hub": {
                    "name": "TenxsomAI",
                    "channel_id": os.getenv("YOUTUBE_CHANNEL_ID", "UCHTnKvKvQiglq2_yaOcQiFg"),
                    "role": "hub",
                    "status": "ready_for_oauth"
                },
                "planned_spokes": [
                    {
                        "name": "Tenxsom Tech News",
                        "role": "spoke",
                        "archetype": "tech_news_analysis",
                        "status": "planned"
                    },
                    {
                        "name": "Tenxsom Morphs",
                        "role": "spoke", 
                        "archetype": "sensory_asmr_content",
                        "status": "planned"
                    },
                    {
                        "name": "Tenxsom Histories",
                        "role": "spoke",
                        "archetype": "educational_documentary",
                        "status": "planned"
                    },
                    {
                        "name": "Tenxsom Future",
                        "role": "spoke",
                        "archetype": "future_tech_ai",
                        "status": "planned"
                    }
                ]
            }
        }
    
    def step1_prepare_oauth_application(self):
        """Prepare OAuth2 application configuration"""
        print("\n📋 STEP 1: OAuth Application Setup Instructions")
        print("=" * 60)
        
        instructions = {
            "google_cloud_console": {
                "url": "https://console.cloud.google.com",
                "project": "tenxsom-ai-1631088 (or your project)",
                "steps": [
                    "1. Navigate to APIs & Services → Credentials",
                    "2. Click '+ CREATE CREDENTIALS' → OAuth client ID",
                    "3. If prompted, configure OAuth consent screen first:",
                    "   - User Type: External",
                    "   - App name: TenxsomAI Multi-Channel Manager",
                    "   - User support email: Your email",
                    "   - Developer contact: Your email",
                    "   - Scopes: Add YouTube Data API v3 scopes",
                    "4. For OAuth client ID:",
                    "   - Application type: Desktop app",
                    "   - Name: TenxsomAI Multi-Channel OAuth",
                    "5. Download the JSON file"
                ]
            },
            "required_scopes": [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.force-ssl",
                "https://www.googleapis.com/auth/youtube.readonly",
                "https://www.googleapis.com/auth/youtubepartner"
            ],
            "api_enablement": [
                "YouTube Data API v3",
                "YouTube Analytics API",
                "YouTube Reporting API"
            ]
        }
        
        # Print instructions
        print("\n🌐 Google Cloud Console Setup:")
        print(f"   URL: {instructions['google_cloud_console']['url']}")
        print(f"   Project: {instructions['google_cloud_console']['project']}")
        
        print("\n📝 Setup Steps:")
        for step in instructions['google_cloud_console']['steps']:
            print(f"   {step}")
        
        print("\n🔑 Required OAuth Scopes:")
        for scope in instructions['required_scopes']:
            print(f"   • {scope}")
        
        print("\n⚡ APIs to Enable:")
        for api in instructions['api_enablement']:
            print(f"   • {api}")
        
        # Save instructions for reference
        with open("oauth_setup_instructions.json", "w") as f:
            json.dump(instructions, f, indent=2)
        
        print(f"\n💾 Instructions saved to: oauth_setup_instructions.json")
        
        self.setup_log.append({
            "step": "OAuth Application Instructions",
            "status": "provided",
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def step2_validate_client_secrets(self):
        """Validate client secrets file"""
        print("\n🔍 STEP 2: Validate Client Secrets")
        print("=" * 40)
        
        client_secrets_path = "youtube-upload-pipeline/auth/client_secrets.json"
        
        if os.path.exists(client_secrets_path):
            try:
                with open(client_secrets_path, 'r') as f:
                    secrets = json.load(f)
                
                # Check structure
                if "installed" in secrets or "web" in secrets:
                    app_type = "installed" if "installed" in secrets else "web"
                    client_data = secrets[app_type]
                    
                    client_id = client_data.get("client_id", "")
                    project_id = client_data.get("project_id", "")
                    
                    print(f"✅ Client secrets file found and valid")
                    print(f"   Type: {app_type}")
                    print(f"   Client ID: ...{client_id[-30:]}")
                    print(f"   Project ID: {project_id}")
                    
                    # Check if it's configured for multi-channel
                    if "Multi-Channel" in client_id or "multi" in client_id.lower():
                        print(f"   ✅ Appears to be multi-channel OAuth app")
                    else:
                        print(f"   ⚠️  May need to create new multi-channel OAuth app")
                    
                    self.setup_log.append({
                        "step": "Client Secrets Validation",
                        "status": "valid",
                        "client_id_suffix": client_id[-30:],
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    return True
                else:
                    print("❌ Invalid client secrets structure")
                    return False
                    
            except Exception as e:
                print(f"❌ Error reading client secrets: {e}")
                return False
        else:
            print(f"❌ Client secrets file not found at: {client_secrets_path}")
            print("\n📋 Next steps:")
            print("1. Complete Google Cloud Console setup")
            print("2. Download OAuth2 credentials JSON")
            print("3. Save as: youtube-upload-pipeline/auth/client_secrets.json")
            return False
    
    def step3_create_channel_token_manager(self):
        """Create channel token management structure"""
        print("\n🏗️ STEP 3: Create Channel Token Manager")
        print("=" * 40)
        
        # Create token manager code
        token_manager_code = '''#!/usr/bin/env python3
"""
Multi-Channel Token Manager for YouTube OAuth
Manages refresh tokens for multiple YouTube channels
"""

import os
import json
import logging
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class MultiChannelTokenManager:
    """Manages OAuth tokens for multiple YouTube channels"""
    
    def __init__(self):
        self.token_store_path = Path("youtube-upload-pipeline/auth/channel_tokens")
        self.token_store_path.mkdir(parents=True, exist_ok=True)
        
        # Channel mapping
        self.channel_mapping = {
            "hub": {
                "channel_name": "TenxsomAI",
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_HUB"),
                "token_file": "token_hub.json",
                "role": "hub"
            },
            "tech": {
                "channel_name": "Tenxsom Tech News",
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_TECH"),
                "token_file": "token_tech.json",
                "role": "spoke"
            },
            "morphs": {
                "channel_name": "Tenxsom Morphs",
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_MORPHS"),
                "token_file": "token_morphs.json",
                "role": "spoke"
            },
            "histories": {
                "channel_name": "Tenxsom Histories", 
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_HISTORIES"),
                "token_file": "token_histories.json",
                "role": "spoke"
            },
            "future": {
                "channel_name": "Tenxsom Future",
                "channel_id": os.getenv("YOUTUBE_CHANNEL_ID_FUTURE"),
                "token_file": "token_future.json",
                "role": "spoke"
            }
        }
        
        # OAuth scopes
        self.scopes = [
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.force-ssl",
            "https://www.googleapis.com/auth/youtube.readonly"
        ]
    
    def get_channel_service(self, channel_key: str):
        """Get YouTube service for specific channel"""
        if channel_key not in self.channel_mapping:
            raise ValueError(f"Unknown channel key: {channel_key}")
        
        channel_info = self.channel_mapping[channel_key]
        token_path = self.token_store_path / channel_info["token_file"]
        
        # Load credentials
        if not token_path.exists():
            # Try legacy token location
            legacy_token = Path("youtube-upload-pipeline/auth/token.json")
            if legacy_token.exists() and channel_key == "hub":
                logger.info("Using legacy token for hub channel")
                token_path = legacy_token
            else:
                raise FileNotFoundError(
                    f"No token found for channel: {channel_info['channel_name']}. "
                    f"Please run OAuth flow for this channel."
                )
        
        # Load and refresh credentials
        credentials = Credentials.from_authorized_user_file(
            str(token_path), self.scopes
        )
        
        if credentials.expired and credentials.refresh_token:
            logger.info(f"Refreshing token for {channel_info['channel_name']}")
            credentials.refresh(Request())
            
            # Save refreshed token
            with open(token_path, 'w') as f:
                f.write(credentials.to_json())
        
        # Build service
        youtube = build('youtube', 'v3', credentials=credentials)
        
        logger.info(f"YouTube service created for: {channel_info['channel_name']}")
        return youtube, channel_info
    
    def list_available_channels(self) -> Dict[str, Dict]:
        """List all configured channels and their token status"""
        channel_status = {}
        
        for key, info in self.channel_mapping.items():
            token_path = self.token_store_path / info["token_file"]
            
            # Check legacy location for hub
            if not token_path.exists() and key == "hub":
                legacy_token = Path("youtube-upload-pipeline/auth/token.json")
                if legacy_token.exists():
                    token_path = legacy_token
            
            channel_status[key] = {
                "name": info["channel_name"],
                "role": info["role"],
                "token_exists": token_path.exists(),
                "token_path": str(token_path),
                "ready": token_path.exists()
            }
        
        return channel_status
    
    def route_content_to_channel(self, archetype: str) -> str:
        """Route content to appropriate channel based on archetype"""
        archetype_to_channel = {
            "tech_news_analysis": "tech",
            "sensory_asmr_content": "morphs",
            "educational_documentary": "histories",
            "future_tech_ai": "future",
            "hub_incubator": "hub"
        }
        
        channel_key = archetype_to_channel.get(archetype, "hub")
        
        # Check if spoke channel is ready, fallback to hub
        channel_status = self.list_available_channels()
        if not channel_status[channel_key]["ready"]:
            logger.info(f"Spoke channel {channel_key} not ready, routing to hub")
            return "hub"
        
        return channel_key
    
    def get_network_analytics(self) -> Dict:
        """Get analytics across all channels"""
        network_stats = {
            "timestamp": datetime.now().isoformat(),
            "channels": {},
            "total_ready": 0,
            "total_configured": len(self.channel_mapping)
        }
        
        for key, status in self.list_available_channels().items():
            if status["ready"]:
                network_stats["total_ready"] += 1
                
                try:
                    youtube, channel_info = self.get_channel_service(key)
                    
                    # Get channel statistics
                    response = youtube.channels().list(
                        part="statistics,snippet",
                        id=channel_info["channel_id"] or "mine"
                    ).execute()
                    
                    if response["items"]:
                        stats = response["items"][0]["statistics"]
                        network_stats["channels"][key] = {
                            "name": channel_info["channel_name"],
                            "subscribers": int(stats.get("subscriberCount", 0)),
                            "views": int(stats.get("viewCount", 0)),
                            "videos": int(stats.get("videoCount", 0))
                        }
                except Exception as e:
                    logger.error(f"Failed to get stats for {key}: {e}")
        
        return network_stats


# Singleton instance
_token_manager = None

def get_token_manager() -> MultiChannelTokenManager:
    """Get singleton token manager instance"""
    global _token_manager
    if _token_manager is None:
        _token_manager = MultiChannelTokenManager()
    return _token_manager
'''
        
        # Save token manager
        token_manager_path = "youtube-upload-pipeline/services/multi_channel_token_manager.py"
        os.makedirs(os.path.dirname(token_manager_path), exist_ok=True)
        
        with open(token_manager_path, "w") as f:
            f.write(token_manager_code)
        
        print(f"✅ Created multi-channel token manager")
        print(f"   Path: {token_manager_path}")
        
        # Create token storage directory
        token_store = Path("youtube-upload-pipeline/auth/channel_tokens")
        token_store.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created token storage directory: {token_store}")
        
        self.setup_log.append({
            "step": "Token Manager Creation",
            "status": "completed",
            "files_created": [token_manager_path, str(token_store)],
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def step4_create_oauth_flow_script(self):
        """Create OAuth flow script for multi-channel"""
        print("\n📝 STEP 4: Create Multi-Channel OAuth Flow Script")
        print("=" * 40)
        
        oauth_flow_code = '''#!/usr/bin/env python3
"""
Multi-Channel OAuth Flow
Run this to authenticate each YouTube channel
"""

import os
import sys
import json
from pathlib import Path

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
except ImportError:
    print("❌ Missing required libraries. Please install:")
    print("pip install google-auth-oauthlib google-auth-httplib2")
    sys.exit(1)

# Configuration
CLIENT_SECRETS_FILE = "youtube-upload-pipeline/auth/client_secrets.json"
TOKEN_STORE_PATH = Path("youtube-upload-pipeline/auth/channel_tokens")
TOKEN_STORE_PATH.mkdir(parents=True, exist_ok=True)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

CHANNELS = {
    "hub": {
        "name": "TenxsomAI",
        "description": "Main hub channel",
        "token_file": "token_hub.json"
    },
    "tech": {
        "name": "Tenxsom Tech News",
        "description": "Tech news and analysis",
        "token_file": "token_tech.json"
    },
    "morphs": {
        "name": "Tenxsom Morphs",
        "description": "Sensory and ASMR content",
        "token_file": "token_morphs.json"
    },
    "histories": {
        "name": "Tenxsom Histories",
        "description": "Educational documentaries",
        "token_file": "token_histories.json"
    },
    "future": {
        "name": "Tenxsom Future",
        "description": "Future tech and AI",
        "token_file": "token_future.json"
    }
}

def authenticate_channel(channel_key: str):
    """Authenticate a specific channel"""
    if channel_key not in CHANNELS:
        print(f"❌ Unknown channel: {channel_key}")
        return False
    
    channel = CHANNELS[channel_key]
    print(f"\\n🔐 Authenticating: {channel['name']}")
    print(f"   Description: {channel['description']}")
    
    # Check if token already exists
    token_path = TOKEN_STORE_PATH / channel['token_file']
    if token_path.exists():
        print(f"   ✅ Token already exists: {token_path}")
        response = input("   Replace existing token? (y/N): ").lower()
        if response != 'y':
            return True
    
    # Run OAuth flow
    print("\\n📌 Opening browser for authentication...")
    print("   Please sign in with the YouTube account that owns this channel")
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES
        )
        credentials = flow.run_local_server(port=0)
        
        if credentials and credentials.refresh_token:
            # Save token
            with open(token_path, 'w') as f:
                f.write(credentials.to_json())
            
            print(f"\\n✅ Authentication successful!")
            print(f"   Token saved to: {token_path}")
            
            # Also save refresh token separately for Secret Manager
            refresh_token_path = TOKEN_STORE_PATH / f"refresh_{channel_key}.txt"
            with open(refresh_token_path, 'w') as f:
                f.write(credentials.refresh_token)
            
            print(f"   Refresh token saved to: {refresh_token_path}")
            print(f"   ⚠️  Upload this to Secret Manager as: youtube-refresh-token-{channel_key}")
            
            return True
        else:
            print("❌ Authentication failed - no refresh token received")
            return False
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return False

def main():
    """Main authentication flow"""
    print("🎬 TENXSOMAI MULTI-CHANNEL OAUTH SETUP")
    print("=" * 50)
    
    # Check client secrets
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"❌ Client secrets not found: {CLIENT_SECRETS_FILE}")
        print("\\nPlease:")
        print("1. Complete Google Cloud Console OAuth setup")
        print("2. Download credentials JSON")
        print(f"3. Save as: {CLIENT_SECRETS_FILE}")
        return
    
    # Show available channels
    print("\\n📺 Available Channels:")
    for key, channel in CHANNELS.items():
        token_path = TOKEN_STORE_PATH / channel['token_file']
        status = "✅ Authenticated" if token_path.exists() else "❌ Not authenticated"
        print(f"   {key}: {channel['name']} - {status}")
    
    # Authentication menu
    while True:
        print("\\n🔑 Authentication Options:")
        print("1. Authenticate hub channel (TenxsomAI)")
        print("2. Authenticate all channels")
        print("3. Authenticate specific channel")
        print("4. Show channel status")
        print("5. Exit")
        
        choice = input("\\nSelect option (1-5): ").strip()
        
        if choice == "1":
            authenticate_channel("hub")
        elif choice == "2":
            print("\\n🔄 Authenticating all channels...")
            for key in CHANNELS:
                if not authenticate_channel(key):
                    print(f"⚠️  Failed to authenticate {key}, continuing...")
        elif choice == "3":
            print("\\nChannel keys:", ", ".join(CHANNELS.keys()))
            key = input("Enter channel key: ").strip()
            authenticate_channel(key)
        elif choice == "4":
            print("\\n📊 Channel Authentication Status:")
            for key, channel in CHANNELS.items():
                token_path = TOKEN_STORE_PATH / channel['token_file']
                status = "✅" if token_path.exists() else "❌"
                print(f"   {status} {key}: {channel['name']}")
        elif choice == "5":
            break
    
    print("\\n✅ OAuth setup complete!")
    print("\\n🚀 Next steps:")
    print("1. Upload refresh tokens to Google Secret Manager")
    print("2. Test upload to hub channel")
    print("3. Implement channel routing logic")

if __name__ == "__main__":
    main()
'''
        
        # Save OAuth flow script
        oauth_script_path = "multi_channel_oauth_flow.py"
        with open(oauth_script_path, "w") as f:
            f.write(oauth_flow_code)
        
        os.chmod(oauth_script_path, 0o755)  # Make executable
        
        print(f"✅ Created multi-channel OAuth flow script")
        print(f"   Path: {oauth_script_path}")
        print(f"   Run: python3 {oauth_script_path}")
        
        self.setup_log.append({
            "step": "OAuth Flow Script Creation",
            "status": "completed",
            "script_path": oauth_script_path,
            "timestamp": datetime.now().isoformat()
        })
        
        return True
    
    def run_setup(self):
        """Run complete multi-channel OAuth setup"""
        print("🚀 MULTI-CHANNEL OAUTH SETUP")
        print("=" * 60)
        print("Setting up single OAuth application for all TenxsomAI channels")
        print("=" * 60)
        
        # Step 1: OAuth application instructions
        self.step1_prepare_oauth_application()
        
        # Step 2: Validate existing setup
        has_secrets = self.step2_validate_client_secrets()
        
        # Step 3: Create token manager
        self.step3_create_channel_token_manager()
        
        # Step 4: Create OAuth flow script
        self.step4_create_oauth_flow_script()
        
        # Save setup log
        with open("multi_channel_oauth_setup_log.json", "w") as f:
            json.dump({
                "setup_timestamp": datetime.now().isoformat(),
                "oauth_config": self.oauth_config,
                "setup_log": self.setup_log,
                "has_client_secrets": has_secrets
            }, f, indent=2)
        
        print("\n" + "=" * 60)
        print("✅ MULTI-CHANNEL OAUTH SETUP COMPLETE!")
        print("=" * 60)
        
        if has_secrets:
            print("\n🎉 Client secrets already configured!")
            print("\n🚀 NEXT STEP: Run OAuth flow for hub channel")
            print(f"   Command: python3 multi_channel_oauth_flow.py")
            print("   Select option 1 to authenticate hub channel")
        else:
            print("\n📋 NEXT STEPS:")
            print("1. Complete Google Cloud Console setup (see instructions above)")
            print("2. Download OAuth credentials JSON")
            print("3. Save as: youtube-upload-pipeline/auth/client_secrets.json")
            print("4. Run: python3 multi_channel_oauth_flow.py")
        
        print("\n💡 This setup supports:")
        print("   • 1 hub channel (TenxsomAI)")
        print("   • 4 planned spoke channels")
        print("   • Incremental channel addition")
        print("   • Centralized token management")
        
        return has_secrets


def main():
    """Main setup function"""
    setup = MultiChannelOAuthSetup()
    has_secrets = setup.run_setup()
    
    if has_secrets:
        print("\n✅ Ready to proceed with OAuth authentication!")
        sys.exit(0)
    else:
        print("\n⏸️  Complete Google Cloud Console setup first")
        sys.exit(1)


if __name__ == "__main__":
    main()