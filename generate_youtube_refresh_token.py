#!/usr/bin/env python3
"""
Generate YouTube Refresh Token (One-time setup)
Run this script ONCE on a machine with browser access to generate the refresh token
"""

import os
import sys
from pathlib import Path

# Check if we have the required libraries
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
except ImportError:
    print("❌ Missing required libraries. Please install:")
    print("pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configuration
CLIENT_SECRETS_FILE = "youtube-upload-pipeline/auth/client_secrets.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly"
]

def main():
    """Generate refresh token for YouTube API access"""
    print("🔑 YouTube OAuth2 Refresh Token Generator")
    print("=" * 50)
    
    # Check if client secrets file exists
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"❌ Client secrets file not found: {CLIENT_SECRETS_FILE}")
        print("\nPlease ensure you have:")
        print("1. Created OAuth 2.0 credentials in Google Cloud Console")
        print("2. Downloaded the JSON file as 'client_secrets.json'")
        print("3. Placed it in the youtube-upload-pipeline/auth/ directory")
        return False
    
    print(f"✅ Found client secrets file: {CLIENT_SECRETS_FILE}")
    print("\n🚀 Starting OAuth flow...")
    print("📌 Your browser will open shortly for authentication")
    print("🔐 Please sign in with the YouTube channel owner account")
    
    try:
        # Create the flow using the client secrets file
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, 
            SCOPES
        )
        
        # Run the OAuth flow
        credentials = flow.run_local_server(port=8080)
        
        if credentials and credentials.refresh_token:
            print("\n" + "=" * 60)
            print("✅ AUTHORIZATION SUCCESSFUL!")
            print("=" * 60)
            print("\n🔑 YOUR REFRESH TOKEN:")
            print("=" * 30)
            print(credentials.refresh_token)
            print("=" * 30)
            
            print("\n⚠️  IMPORTANT SECURITY INSTRUCTIONS:")
            print("1. 🔒 COPY the refresh token above")
            print("2. 🏛️  STORE it in Google Secret Manager as 'youtube-refresh-token'")
            print("3. 🚫 DO NOT commit this token to git or share it")
            print("4. 🗑️  DELETE this output after storing the token securely")
            
            # Also save client credentials info for Secret Manager
            client_secrets_path = Path(CLIENT_SECRETS_FILE)
            if client_secrets_path.exists():
                import json
                with open(client_secrets_path) as f:
                    client_data = json.load(f)
                    
                client_info = client_data.get("installed", {})
                client_id = client_info.get("client_id", "")
                client_secret = client_info.get("client_secret", "")
                
                print(f"\n📋 ADDITIONAL INFO FOR SECRET MANAGER:")
                print(f"Client ID: {client_id}")
                print(f"Client Secret: {client_secret}")
                print("\nStore these as separate secrets:")
                print("- youtube-client-id")
                print("- youtube-client-secret") 
                print("- youtube-refresh-token")
            
            # Save token locally for immediate testing (will be moved to Secret Manager)
            token_file = "youtube-upload-pipeline/auth/token.json"
            with open(token_file, 'w') as f:
                f.write(credentials.to_json())
            
            print(f"\n💾 Token also saved locally to: {token_file}")
            print("   (This is for immediate testing - move to Secret Manager for production)")
            
            return True
            
        else:
            print("❌ Authorization failed - no refresh token received")
            return False
            
    except Exception as e:
        print(f"❌ Authorization failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Setup complete! You can now:")
        print("1. Test YouTube uploads locally")
        print("2. Move credentials to Secret Manager for production")
        print("3. Deploy to Cloud Run with secure access")
    else:
        print("\n💔 Setup failed. Please check the instructions and try again.")
    
    sys.exit(0 if success else 1)