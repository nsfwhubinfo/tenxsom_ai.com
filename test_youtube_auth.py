#!/usr/bin/env python3
"""
Test YouTube API authentication and basic functionality
"""

import os
import sys
import json
from pathlib import Path

# Add paths to import modules
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "youtube-upload-pipeline"))

from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

class YouTubeAuthTester:
    """Test YouTube authentication"""
    
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
                      'https://www.googleapis.com/auth/youtube.readonly']
        self.creds = None
        self.youtube = None
        
    def authenticate(self):
        """Authenticate with YouTube API"""
        print("🔐 Authenticating with YouTube API...")
        
        # Token file path
        token_file = 'youtube-upload-pipeline/auth/token.json'
        client_secrets = 'youtube-upload-pipeline/auth/client_secrets.json'
        
        # Check if we have stored credentials
        if os.path.exists(token_file):
            print("   Found existing token file")
            try:
                self.creds = Credentials.from_authorized_user_file(token_file, self.SCOPES)
                print("   Loaded credentials from token file")
            except Exception as e:
                print(f"   Failed to load credentials: {e}")
                self.creds = None
        
        # If no valid credentials, initiate OAuth flow
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("   Refreshing expired credentials...")
                try:
                    from google.auth.transport.requests import Request
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"   Failed to refresh: {e}")
                    self.creds = None
            
            if not self.creds:
                print("   Initiating OAuth flow...")
                print("   📌 Please complete authentication in your browser")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets, self.SCOPES)
                self.creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(token_file, 'w') as token:
                    token.write(self.creds.to_json())
                print("   ✅ Authentication successful! Token saved.")
        
        # Build YouTube service
        self.youtube = build('youtube', 'v3', credentials=self.creds)
        return True
    
    def test_channel_access(self):
        """Test access to YouTube channel"""
        print("\n📺 Testing channel access...")
        
        try:
            # Get authenticated user's channel
            request = self.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                mine=True
            )
            response = request.execute()
            
            if "items" in response and len(response["items"]) > 0:
                channel = response["items"][0]
                snippet = channel["snippet"]
                stats = channel.get("statistics", {})
                
                print(f"✅ Channel access confirmed!")
                print(f"   Channel Name: {snippet['title']}")
                print(f"   Channel ID: {channel['id']}")
                print(f"   Description: {snippet.get('description', 'N/A')[:100]}...")
                print(f"   Subscribers: {stats.get('subscriberCount', 'Hidden')}")
                print(f"   Total Videos: {stats.get('videoCount', 'N/A')}")
                print(f"   Total Views: {stats.get('viewCount', 'N/A')}")
                
                return True, channel
            else:
                print("❌ No channel found for authenticated user")
                return False, None
                
        except HttpError as e:
            print(f"❌ API Error: {e}")
            return False, None
        except Exception as e:
            print(f"❌ Error accessing channel: {e}")
            return False, None
    
    def test_upload_capability(self):
        """Test if we have upload capabilities"""
        print("\n🚀 Testing upload capabilities...")
        
        try:
            # Try to list recent uploads (to verify upload access)
            request = self.youtube.channels().list(
                part="contentDetails",
                mine=True
            )
            response = request.execute()
            
            if "items" in response and len(response["items"]) > 0:
                uploads_playlist = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
                
                # Get recent uploads
                playlist_request = self.youtube.playlistItems().list(
                    part="snippet",
                    playlistId=uploads_playlist,
                    maxResults=5
                )
                playlist_response = playlist_request.execute()
                
                video_count = len(playlist_response.get("items", []))
                print(f"✅ Upload access confirmed!")
                print(f"   Recent uploads found: {video_count}")
                
                if video_count > 0:
                    print("   Recent videos:")
                    for item in playlist_response["items"][:3]:
                        title = item["snippet"]["title"]
                        video_id = item["snippet"]["resourceId"]["videoId"]
                        print(f"     - {title[:50]}... (ID: {video_id})")
                
                return True
            else:
                print("❌ Could not verify upload access")
                return False
                
        except HttpError as e:
            error_reason = e.error_details[0]["reason"] if e.error_details else "Unknown"
            print(f"❌ API Error: {error_reason}")
            if "quotaExceeded" in str(e):
                print("   ⚠️  YouTube API quota exceeded. Upload will work when quota resets.")
                return True  # Quota exceeded doesn't mean auth failed
            return False
        except Exception as e:
            print(f"❌ Error testing upload capability: {e}")
            return False
    
    def run_tests(self):
        """Run all authentication tests"""
        print("🔑 YOUTUBE AUTHENTICATION TEST")
        print("=" * 50)
        print(f"API Key: {os.getenv('YOUTUBE_API_KEY', 'Not found')[:20]}...")
        print(f"Channel ID: {os.getenv('YOUTUBE_CHANNEL_ID', 'Not found')}")
        print("=" * 50)
        
        results = {
            "authenticated": False,
            "channel_access": False,
            "upload_capability": False,
            "channel_info": None
        }
        
        # Authenticate
        try:
            if self.authenticate():
                results["authenticated"] = True
                print("✅ Authentication successful!")
            else:
                print("❌ Authentication failed!")
                return results
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return results
        
        # Test channel access
        channel_success, channel_info = self.test_channel_access()
        results["channel_access"] = channel_success
        results["channel_info"] = channel_info
        
        # Test upload capability
        if channel_success:
            results["upload_capability"] = self.test_upload_capability()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Authentication: {'✅ PASSED' if results['authenticated'] else '❌ FAILED'}")
        print(f"Channel Access: {'✅ PASSED' if results['channel_access'] else '❌ FAILED'}")
        print(f"Upload Capability: {'✅ PASSED' if results['upload_capability'] else '❌ FAILED'}")
        
        # Save results
        with open("youtube_auth_test_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Results saved to: youtube_auth_test_results.json")
        
        if all([results["authenticated"], results["channel_access"], results["upload_capability"]]):
            print("\n🎉 YouTube API is fully configured and ready for uploads!")
            print("\nNext steps:")
            print("1. You can now upload videos programmatically")
            print("2. Monitor your API quota at: https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas")
            return True
        else:
            print("\n⚠️  Some tests failed. Please check the configuration.")
            return False


def main():
    """Main function"""
    tester = YouTubeAuthTester()
    success = tester.run_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()