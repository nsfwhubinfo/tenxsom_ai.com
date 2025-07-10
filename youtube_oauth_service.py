#!/usr/bin/env python3
"""
Production YouTube OAuth2 Service
Uses refresh token for headless authentication in Cloud Run
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)

class YouTubeOAuthService:
    """Production YouTube service using OAuth2 refresh token"""
    
    def __init__(self):
        self.youtube = None
        self.credentials = None
        self._initialize_credentials()
    
    def _initialize_credentials(self):
        """Initialize credentials from refresh token"""
        try:
            # Try to load from local token file first (for testing)
            token_file = "youtube-upload-pipeline/auth/token.json"
            if os.path.exists(token_file):
                print("📁 Loading credentials from local token file...")
                self.credentials = Credentials.from_authorized_user_file(
                    token_file,
                    scopes=[
                        "https://www.googleapis.com/auth/youtube.upload",
                        "https://www.googleapis.com/auth/youtube.force-ssl",
                        "https://www.googleapis.com/auth/youtube.readonly"
                    ]
                )
            else:
                # Production: Load from environment variables (Secret Manager)
                print("🔐 Loading credentials from environment...")
                client_id = os.getenv("YOUTUBE_CLIENT_ID")
                client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
                refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
                
                if not all([client_id, client_secret, refresh_token]):
                    missing = []
                    if not client_id: missing.append("YOUTUBE_CLIENT_ID")
                    if not client_secret: missing.append("YOUTUBE_CLIENT_SECRET")
                    if not refresh_token: missing.append("YOUTUBE_REFRESH_TOKEN")
                    
                    raise Exception(f"Missing environment variables: {', '.join(missing)}")
                
                self.credentials = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=[
                        "https://www.googleapis.com/auth/youtube.upload",
                        "https://www.googleapis.com/auth/youtube.force-ssl",
                        "https://www.googleapis.com/auth/youtube.readonly"
                    ]
                )
            
            # Refresh credentials if needed
            if self.credentials.expired:
                print("🔄 Refreshing expired credentials...")
                self.credentials.refresh(Request())
            
            # Build YouTube service
            self.youtube = build("youtube", "v3", credentials=self.credentials)
            print("✅ YouTube service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize YouTube credentials: {e}")
            raise
    
    def get_channel_info(self) -> Dict[str, Any]:
        """Get authenticated user's channel information"""
        try:
            request = self.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                mine=True
            )
            response = request.execute()
            
            if "items" in response and len(response["items"]) > 0:
                return response["items"][0]
            else:
                raise Exception("No channel found for authenticated user")
                
        except HttpError as e:
            logger.error(f"YouTube API error getting channel info: {e}")
            raise
    
    def upload_video(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list = None,
        category_id: str = "22",
        privacy_status: str = "private",
        thumbnail_path: Optional[str] = None
    ) -> str:
        """Upload video to YouTube and return video ID"""
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Prepare video metadata
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or [],
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False
            }
        }
        
        # Prepare media upload
        media = MediaFileUpload(
            video_path,
            chunksize=-1,
            resumable=True,
            mimetype="video/*"
        )
        
        try:
            print(f"📤 Uploading video: {title}")
            
            # Insert video
            insert_request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = insert_request.execute()
            video_id = response["id"]
            
            print(f"✅ Video uploaded successfully!")
            print(f"   Video ID: {video_id}")
            print(f"   URL: https://www.youtube.com/watch?v={video_id}")
            
            # Upload thumbnail if provided
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    self.upload_thumbnail(video_id, thumbnail_path)
                except Exception as e:
                    logger.warning(f"Thumbnail upload failed: {e}")
            
            return video_id
            
        except HttpError as e:
            logger.error(f"YouTube upload failed: {e}")
            raise
    
    def upload_thumbnail(self, video_id: str, thumbnail_path: str):
        """Upload custom thumbnail for video"""
        try:
            media = MediaFileUpload(thumbnail_path, mimetype="image/*")
            
            request = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=media
            )
            
            response = request.execute()
            print(f"✅ Thumbnail uploaded for video {video_id}")
            return response
            
        except HttpError as e:
            logger.error(f"Thumbnail upload failed: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test YouTube API connection"""
        try:
            channel_info = self.get_channel_info()
            channel_name = channel_info["snippet"]["title"]
            subscriber_count = channel_info.get("statistics", {}).get("subscriberCount", "Hidden")
            
            print(f"✅ Connected to YouTube channel: {channel_name}")
            print(f"   Subscribers: {subscriber_count}")
            return True
            
        except Exception as e:
            print(f"❌ YouTube connection test failed: {e}")
            return False


# Example usage and testing
async def test_youtube_service():
    """Test the YouTube OAuth service"""
    print("🔍 Testing YouTube OAuth Service")
    print("=" * 40)
    
    try:
        service = YouTubeOAuthService()
        
        # Test connection
        if service.test_connection():
            print("✅ YouTube service is ready for uploads!")
            return True
        else:
            print("❌ YouTube service connection failed")
            return False
            
    except Exception as e:
        print(f"❌ YouTube service initialization failed: {e}")
        return False


if __name__ == "__main__":
    import asyncio
    success = asyncio.run(test_youtube_service())
    exit(0 if success else 1)