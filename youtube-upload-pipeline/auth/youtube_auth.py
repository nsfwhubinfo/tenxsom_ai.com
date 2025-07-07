#!/usr/bin/env python3

"""
YouTube Authentication Service
Handles OAuth 2.0 authentication for YouTube Data API v3
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeAuthenticator:
    """Handles YouTube API authentication and credential management"""
    
    # YouTube API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.upload',
        'https://www.googleapis.com/auth/youtube',
        'https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/youtubepartner'
    ]
    
    def __init__(self, credentials_dir: str = None):
        """Initialize authenticator with credentials directory"""
        if credentials_dir is None:
            credentials_dir = Path(__file__).parent / "credentials"
        
        self.credentials_dir = Path(credentials_dir)
        self.credentials_dir.mkdir(exist_ok=True)
        
        self.client_secrets_file = self.credentials_dir.parent / "client_secrets.json"
        self.token_file = self.credentials_dir / "token.pickle"
        
        self.credentials = None
        self.service = None
    
    def authenticate(self, force_refresh: bool = False) -> bool:
        """
        Authenticate with YouTube API
        
        Args:
            force_refresh: Force re-authentication even if valid credentials exist
            
        Returns:
            bool: True if authentication successful
        """
        logger.info("Starting YouTube API authentication...")
        
        # Load existing credentials
        if not force_refresh and self.token_file.exists():
            logger.info("Loading existing credentials...")
            try:
                with open(self.token_file, 'rb') as token:
                    self.credentials = pickle.load(token)
                    
                if self.credentials and self.credentials.valid:
                    logger.info("✅ Existing credentials are valid")
                    return self._build_service()
                    
            except Exception as e:
                logger.warning(f"Failed to load existing credentials: {e}")
        
        # Refresh expired credentials
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            logger.info("Refreshing expired credentials...")
            try:
                self.credentials.refresh(Request())
                self._save_credentials()
                logger.info("✅ Credentials refreshed successfully")
                return self._build_service()
                
            except Exception as e:
                logger.warning(f"Failed to refresh credentials: {e}")
        
        # Perform new OAuth flow
        return self._perform_oauth_flow()
    
    def _perform_oauth_flow(self) -> bool:
        """Perform OAuth 2.0 authorization flow"""
        logger.info("Starting OAuth 2.0 flow...")
        
        if not self.client_secrets_file.exists():
            logger.error(f"❌ Client secrets file not found: {self.client_secrets_file}")
            logger.error("Please download client_secrets.json from Google Cloud Console")
            return False
        
        try:
            # Create OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                str(self.client_secrets_file), 
                self.SCOPES
            )
            
            # Run local server for OAuth callback
            logger.info("🌐 Opening browser for OAuth authorization...")
            logger.info("Please authorize the application in your browser")
            
            self.credentials = flow.run_local_server(
                port=8080,
                prompt='consent',
                authorization_prompt_message='Please visit this URL to authorize this application: {url}',
                success_message='The auth flow is complete; you may close this window.',
                open_browser=True
            )
            
            if self.credentials:
                self._save_credentials()
                logger.info("✅ OAuth authentication successful")
                return self._build_service()
            else:
                logger.error("❌ OAuth authentication failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ OAuth flow failed: {e}")
            return False
    
    def _save_credentials(self):
        """Save credentials to file"""
        try:
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.credentials, token)
            logger.info(f"Credentials saved to {self.token_file}")
        except Exception as e:
            logger.error(f"Failed to save credentials: {e}")
    
    def _build_service(self) -> bool:
        """Build YouTube API service"""
        try:
            self.service = build('youtube', 'v3', credentials=self.credentials)
            logger.info("✅ YouTube API service initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to build YouTube service: {e}")
            return False
    
    def get_service(self):
        """Get authenticated YouTube service"""
        if not self.service:
            if not self.authenticate():
                raise Exception("Failed to authenticate with YouTube API")
        return self.service
    
    def test_connection(self) -> dict:
        """Test API connection and return channel information"""
        logger.info("Testing YouTube API connection...")
        
        try:
            service = self.get_service()
            
            # Get channel information
            request = service.channels().list(part='snippet,statistics', mine=True)
            response = request.execute()
            
            if response.get('items'):
                channel = response['items'][0]
                channel_info = {
                    'id': channel['id'],
                    'title': channel['snippet']['title'],
                    'description': channel['snippet']['description'][:100] + '...' if len(channel['snippet']['description']) > 100 else channel['snippet']['description'],
                    'subscriber_count': channel['statistics'].get('subscriberCount', 'Hidden'),
                    'video_count': channel['statistics'].get('videoCount', '0'),
                    'view_count': channel['statistics'].get('viewCount', '0')
                }
                
                logger.info("✅ API connection successful")
                logger.info(f"Channel: {channel_info['title']}")
                logger.info(f"Subscribers: {channel_info['subscriber_count']}")
                logger.info(f"Videos: {channel_info['video_count']}")
                
                return {
                    'status': 'success',
                    'channel': channel_info
                }
            else:
                logger.error("❌ No channel found for authenticated user")
                return {
                    'status': 'error',
                    'message': 'No YouTube channel found'
                }
                
        except HttpError as e:
            logger.error(f"❌ YouTube API error: {e}")
            return {
                'status': 'error',
                'message': f'API error: {e}'
            }
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return {
                'status': 'error',
                'message': f'Connection failed: {e}'
            }
    
    def get_quota_usage(self) -> dict:
        """Get current API quota usage information"""
        # Note: YouTube API doesn't provide direct quota usage endpoint
        # This is an estimation based on typical operations
        logger.info("Checking API quota usage...")
        
        return {
            'daily_limit': 10000,
            'estimated_used': 0,  # Would need to track usage manually
            'remaining': 10000,
            'upload_cost': 1600,
            'thumbnail_cost': 50,
            'max_daily_uploads': 6,
            'note': 'Quota usage must be tracked manually'
        }
    
    def revoke_credentials(self):
        """Revoke and delete stored credentials"""
        logger.info("Revoking credentials...")
        
        try:
            if self.credentials:
                # Revoke the credentials
                self.credentials.revoke(Request())
            
            # Delete token file
            if self.token_file.exists():
                self.token_file.unlink()
                
            self.credentials = None
            self.service = None
            
            logger.info("✅ Credentials revoked successfully")
            
        except Exception as e:
            logger.error(f"Error revoking credentials: {e}")

def main():
    """Test authentication functionality"""
    print("🔐 YouTube API Authentication Test")
    print("=" * 50)
    
    # Initialize authenticator
    auth = YouTubeAuthenticator()
    
    # Test authentication
    if auth.authenticate():
        print("✅ Authentication successful!")
        
        # Test connection
        result = auth.test_connection()
        
        if result['status'] == 'success':
            channel = result['channel']
            print(f"\n📺 Channel Information:")
            print(f"   Title: {channel['title']}")
            print(f"   ID: {channel['id']}")
            print(f"   Subscribers: {channel['subscriber_count']}")
            print(f"   Videos: {channel['video_count']}")
            print(f"   Total Views: {channel['view_count']}")
            
            # Show quota info
            quota = auth.get_quota_usage()
            print(f"\n📊 API Quota Information:")
            print(f"   Daily Limit: {quota['daily_limit']} units")
            print(f"   Upload Cost: {quota['upload_cost']} units per video")
            print(f"   Thumbnail Cost: {quota['thumbnail_cost']} units per thumbnail")
            print(f"   Max Daily Uploads: {quota['max_daily_uploads']} videos")
            
        else:
            print(f"❌ Connection test failed: {result['message']}")
    else:
        print("❌ Authentication failed")
        print("\nTroubleshooting:")
        print("1. Ensure client_secrets.json is in auth/ directory")
        print("2. Check that YouTube Data API v3 is enabled in Google Cloud Console")
        print("3. Verify OAuth consent screen is configured")

if __name__ == "__main__":
    main()