#!/usr/bin/env python3
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
    print(f"\n🔐 Authenticating: {channel['name']}")
    print(f"   Description: {channel['description']}")
    
    # Check if token already exists
    token_path = TOKEN_STORE_PATH / channel['token_file']
    if token_path.exists():
        print(f"   ✅ Token already exists: {token_path}")
        response = input("   Replace existing token? (y/N): ").lower()
        if response != 'y':
            return True
    
    # Run OAuth flow
    print("\n📌 Opening browser for authentication...")
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
            
            print(f"\n✅ Authentication successful!")
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
        print("\nPlease:")
        print("1. Complete Google Cloud Console OAuth setup")
        print("2. Download credentials JSON")
        print(f"3. Save as: {CLIENT_SECRETS_FILE}")
        return
    
    # Show available channels
    print("\n📺 Available Channels:")
    for key, channel in CHANNELS.items():
        token_path = TOKEN_STORE_PATH / channel['token_file']
        status = "✅ Authenticated" if token_path.exists() else "❌ Not authenticated"
        print(f"   {key}: {channel['name']} - {status}")
    
    # Authentication menu
    while True:
        print("\n🔑 Authentication Options:")
        print("1. Authenticate hub channel (TenxsomAI)")
        print("2. Authenticate all channels")
        print("3. Authenticate specific channel")
        print("4. Show channel status")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            authenticate_channel("hub")
        elif choice == "2":
            print("\n🔄 Authenticating all channels...")
            for key in CHANNELS:
                if not authenticate_channel(key):
                    print(f"⚠️  Failed to authenticate {key}, continuing...")
        elif choice == "3":
            print("\nChannel keys:", ", ".join(CHANNELS.keys()))
            key = input("Enter channel key: ").strip()
            authenticate_channel(key)
        elif choice == "4":
            print("\n📊 Channel Authentication Status:")
            for key, channel in CHANNELS.items():
                token_path = TOKEN_STORE_PATH / channel['token_file']
                status = "✅" if token_path.exists() else "❌"
                print(f"   {status} {key}: {channel['name']}")
        elif choice == "5":
            break
    
    print("\n✅ OAuth setup complete!")
    print("\n🚀 Next steps:")
    print("1. Upload refresh tokens to Google Secret Manager")
    print("2. Test upload to hub channel")
    print("3. Implement channel routing logic")

if __name__ == "__main__":
    main()
