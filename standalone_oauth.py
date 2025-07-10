#!/usr/bin/env python3
"""
Standalone OAuth Script for TenxsomAI Hub Channel
This is a self-contained script that can be run anywhere
"""

import os
import sys
import json
from pathlib import Path

# Check for required libraries
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
except ImportError:
    print("❌ Missing required libraries. Please install:")
    print("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# OAuth scopes needed for YouTube
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

def run_oauth_flow():
    """Run OAuth flow for TenxsomAI hub channel"""
    print("🎬 TENXSOMAI HUB CHANNEL OAUTH")
    print("=" * 50)
    
    # Check for client secrets
    if not os.path.exists("client_secrets.json"):
        print("❌ client_secrets.json not found!")
        print("\nPlease ensure client_secrets.json is in the same directory")
        print("as this script before running.")
        return None
    
    print("✅ Found client_secrets.json")
    print("\n🔐 Starting OAuth flow...")
    print("📌 Your browser will open for authentication")
    print("🔑 Please sign in with the YouTube account that owns the TenxsomAI channel")
    
    try:
        # Create flow
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secrets.json", 
            SCOPES
        )
        
        # Run OAuth server
        print("\n🌐 Starting local OAuth server...")
        credentials = flow.run_local_server(
            port=8080,
            authorization_prompt_message='Please visit this URL: {url}',
            success_message='Authentication successful! You may close this window.',
            open_browser=True
        )
        
        if credentials and credentials.refresh_token:
            print("\n✅ Authentication successful!")
            
            # Save full token
            with open("token_hub.json", "w") as f:
                f.write(credentials.to_json())
            print(f"💾 Token saved to: token_hub.json")
            
            # Save refresh token separately
            with open("refresh_token_hub.txt", "w") as f:
                f.write(credentials.refresh_token)
            print(f"💾 Refresh token saved to: refresh_token_hub.txt")
            
            # Display refresh token
            print("\n" + "=" * 60)
            print("🔑 REFRESH TOKEN (KEEP THIS SECURE!):")
            print("=" * 60)
            print(credentials.refresh_token)
            print("=" * 60)
            
            print("\n📋 NEXT STEPS:")
            print("1. Copy token_hub.json to server:")
            print("   scp token_hub.json YOUR_SERVER:/home/golde/tenxsom-ai-vertex/youtube-upload-pipeline/auth/channel_tokens/")
            print("\n2. Or save the refresh token to Google Secret Manager")
            print("\n3. Test the connection on server:")
            print("   python3 test_youtube_connection.py")
            
            return credentials
            
        else:
            print("❌ Authentication failed - no refresh token received")
            return None
            
    except Exception as e:
        print(f"\n❌ OAuth error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're signed into the correct YouTube account")
        print("2. Grant all requested permissions")
        print("3. Try using a different port if 8080 is blocked")
        return None

def main():
    """Main function"""
    print("🚀 TenxsomAI Hub Channel OAuth Setup")
    print("=" * 50)
    print("This script will authenticate the main TenxsomAI channel")
    print("for video uploads and management.")
    print("")
    
    # Run OAuth
    credentials = run_oauth_flow()
    
    if credentials:
        print("\n✅ OAuth setup complete!")
        print("\n🎉 You can now upload videos to TenxsomAI channel!")
        sys.exit(0)
    else:
        print("\n❌ OAuth setup failed")
        print("Please check the errors above and try again")
        sys.exit(1)

if __name__ == "__main__":
    main()