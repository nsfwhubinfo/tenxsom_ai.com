#!/usr/bin/env python3

"""
YouTube Upload Service
Handles video uploads, metadata management, and thumbnail assignment
"""

import os
import sys
import logging
import mimetypes
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from auth.youtube_auth import YouTubeAuthenticator
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
import httplib2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YouTubeUploader:
    """Service for uploading videos to YouTube with metadata and thumbnails"""
    
    # Valid video file types
    VALID_VIDEO_TYPES = [
        'video/mp4', 'video/mpeg', 'video/quicktime', 'video/x-msvideo',
        'video/webm', 'video/x-flv', 'video/3gpp', 'video/x-ms-wmv'
    ]
    
    # Valid privacy statuses
    PRIVACY_STATUSES = ['private', 'public', 'unlisted']
    
    # Category IDs (most common)
    CATEGORIES = {
        'film_animation': 1,
        'autos_vehicles': 2,
        'music': 10,
        'pets_animals': 15,
        'sports': 17,
        'travel_events': 19,
        'gaming': 20,
        'people_blogs': 22,
        'comedy': 23,
        'entertainment': 24,
        'news_politics': 25,
        'howto_style': 26,
        'education': 27,
        'science_technology': 28,
        'nonprofits_activism': 29
    }
    
    def __init__(self, authenticator: YouTubeAuthenticator = None):
        """Initialize uploader with authentication"""
        self.auth = authenticator or YouTubeAuthenticator()
        self.service = None
        
        # Default upload settings
        self.default_settings = {
            'privacy_status': os.getenv('DEFAULT_PRIVACY_STATUS', 'private'),
            'category_id': int(os.getenv('DEFAULT_UPLOAD_CATEGORY', '22')),
            'language': os.getenv('DEFAULT_LANGUAGE', 'en'),
            'default_tags': os.getenv('DEFAULT_TAGS', '').split(',') if os.getenv('DEFAULT_TAGS') else []
        }
    
    def _get_service(self):
        """Get authenticated YouTube service"""
        if not self.service:
            self.service = self.auth.get_service()
        return self.service
    
    def upload_video(self, 
                    video_path: str,
                    title: str,
                    description: str = "",
                    tags: List[str] = None,
                    category_id: int = None,
                    privacy_status: str = None,
                    thumbnail_path: str = None,
                    scheduled_time: datetime = None) -> Dict[str, Any]:
        """
        Upload video to YouTube with metadata
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            category_id: YouTube category ID
            privacy_status: 'private', 'public', or 'unlisted'
            thumbnail_path: Path to thumbnail image
            scheduled_time: When to publish (if privacy_status is 'private')
            
        Returns:
            Dict with upload result information
        """
        logger.info(f"Starting video upload: {title}")
        
        # Validate inputs
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if not self._is_valid_video_file(video_path):
            raise ValueError(f"Invalid video file type: {video_path}")
        
        # Set defaults
        tags = tags or self.default_settings['default_tags']
        category_id = category_id or self.default_settings['category_id']
        privacy_status = privacy_status or self.default_settings['privacy_status']
        
        if privacy_status not in self.PRIVACY_STATUSES:
            raise ValueError(f"Invalid privacy status: {privacy_status}")
        
        try:
            service = self._get_service()
            
            # Prepare video metadata
            video_metadata = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit
                    'description': description[:5000],  # YouTube description limit
                    'tags': tags[:15] if tags else [],  # YouTube tag limit
                    'categoryId': str(category_id),
                    'defaultLanguage': self.default_settings['language']
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Add scheduled publish time if provided
            if scheduled_time and privacy_status == 'private':
                video_metadata['status']['publishAt'] = scheduled_time.isoformat() + 'Z'
            
            # Create media upload
            media = MediaFileUpload(
                str(video_path),
                chunksize=-1,  # Upload in single chunk
                resumable=True,
                mimetype=self._get_video_mimetype(video_path)
            )
            
            # Execute upload
            logger.info("Uploading video to YouTube...")
            
            insert_request = service.videos().insert(
                part=','.join(video_metadata.keys()),
                body=video_metadata,
                media_body=media
            )
            
            # Upload with progress tracking
            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")
            
            video_id = response['id']
            logger.info(f"✅ Video uploaded successfully! Video ID: {video_id}")
            
            # Upload thumbnail if provided
            thumbnail_result = None
            if thumbnail_path:
                thumbnail_result = self.upload_thumbnail(video_id, thumbnail_path)
            
            # Return result
            result = {
                'status': 'success',
                'video_id': video_id,
                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                'title': title,
                'privacy_status': privacy_status,
                'upload_time': datetime.now().isoformat(),
                'thumbnail_uploaded': bool(thumbnail_result),
                'file_size_mb': round(video_path.stat().st_size / (1024 * 1024), 2)
            }
            
            if thumbnail_result:
                result['thumbnail_result'] = thumbnail_result
            
            logger.info(f"Upload complete: {result['video_url']}")
            return result
            
        except HttpError as e:
            error_msg = f"YouTube API error: {e}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'video_id': None
            }
        except Exception as e:
            error_msg = f"Upload failed: {e}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'video_id': None
            }
    
    def upload_thumbnail(self, video_id: str, thumbnail_path: str) -> Dict[str, Any]:
        """
        Upload custom thumbnail for video
        
        Args:
            video_id: YouTube video ID
            thumbnail_path: Path to thumbnail image
            
        Returns:
            Dict with thumbnail upload result
        """
        logger.info(f"Uploading thumbnail for video {video_id}")
        
        thumbnail_path = Path(thumbnail_path)
        if not thumbnail_path.exists():
            raise FileNotFoundError(f"Thumbnail file not found: {thumbnail_path}")
        
        if not self._is_valid_thumbnail(thumbnail_path):
            raise ValueError(f"Invalid thumbnail file: {thumbnail_path}")
        
        try:
            service = self._get_service()
            
            # Upload thumbnail
            service.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(str(thumbnail_path))
            ).execute()
            
            logger.info(f"✅ Thumbnail uploaded successfully for video {video_id}")
            
            return {
                'status': 'success',
                'video_id': video_id,
                'thumbnail_path': str(thumbnail_path),
                'upload_time': datetime.now().isoformat()
            }
            
        except HttpError as e:
            error_msg = f"Thumbnail upload error: {e}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'video_id': video_id
            }
    
    def update_video_metadata(self, 
                             video_id: str, 
                             title: str = None,
                             description: str = None, 
                             tags: List[str] = None,
                             privacy_status: str = None) -> Dict[str, Any]:
        """
        Update video metadata
        
        Args:
            video_id: YouTube video ID
            title: New title
            description: New description
            tags: New tags
            privacy_status: New privacy status
            
        Returns:
            Dict with update result
        """
        logger.info(f"Updating metadata for video {video_id}")
        
        try:
            service = self._get_service()
            
            # Get current video metadata
            current_video = service.videos().list(
                part='snippet,status',
                id=video_id
            ).execute()
            
            if not current_video['items']:
                raise ValueError(f"Video not found: {video_id}")
            
            video_data = current_video['items'][0]
            
            # Update only provided fields
            updates = {}
            
            if title is not None or description is not None or tags is not None:
                snippet = video_data['snippet'].copy()
                if title is not None:
                    snippet['title'] = title[:100]
                if description is not None:
                    snippet['description'] = description[:5000]
                if tags is not None:
                    snippet['tags'] = tags[:15]
                updates['snippet'] = snippet
            
            if privacy_status is not None:
                if privacy_status not in self.PRIVACY_STATUSES:
                    raise ValueError(f"Invalid privacy status: {privacy_status}")
                status = video_data['status'].copy()
                status['privacyStatus'] = privacy_status
                updates['status'] = status
            
            if not updates:
                logger.info("No updates to apply")
                return {'status': 'no_changes', 'video_id': video_id}
            
            # Apply updates
            update_body = {'id': video_id}
            update_body.update(updates)
            
            service.videos().update(
                part=','.join(updates.keys()),
                body=update_body
            ).execute()
            
            logger.info(f"✅ Video metadata updated successfully: {video_id}")
            
            return {
                'status': 'success',
                'video_id': video_id,
                'updates_applied': list(updates.keys()),
                'update_time': datetime.now().isoformat()
            }
            
        except HttpError as e:
            error_msg = f"Update error: {e}"
            logger.error(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'video_id': video_id
            }
    
    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get detailed information about a video"""
        try:
            service = self._get_service()
            
            response = service.videos().list(
                part='snippet,status,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not response['items']:
                return {'status': 'not_found', 'video_id': video_id}
            
            video = response['items'][0]
            
            return {
                'status': 'success',
                'video_id': video_id,
                'title': video['snippet']['title'],
                'description': video['snippet']['description'],
                'privacy_status': video['status']['privacyStatus'],
                'upload_status': video['status']['uploadStatus'],
                'view_count': video['statistics'].get('viewCount', '0'),
                'like_count': video['statistics'].get('likeCount', '0'),
                'comment_count': video['statistics'].get('commentCount', '0'),
                'duration': video['contentDetails']['duration'],
                'published_at': video['snippet']['publishedAt']
            }
            
        except HttpError as e:
            return {
                'status': 'error',
                'error': str(e),
                'video_id': video_id
            }
    
    def _is_valid_video_file(self, file_path: Path) -> bool:
        """Check if file is a valid video type"""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type in self.VALID_VIDEO_TYPES
    
    def _is_valid_thumbnail(self, file_path: Path) -> bool:
        """Check if file is a valid thumbnail"""
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        return file_path.suffix.lower() in valid_extensions
    
    def _get_video_mimetype(self, file_path: Path) -> str:
        """Get MIME type for video file"""
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or 'video/mp4'
    
    def get_upload_quota_cost(self, has_thumbnail: bool = False) -> int:
        """Calculate quota cost for upload"""
        cost = 1600  # Base video upload cost
        if has_thumbnail:
            cost += 50  # Thumbnail upload cost
        return cost

def main():
    """Test upload functionality"""
    print("🎬 YouTube Upload Service Test")
    print("=" * 50)
    
    # Initialize uploader
    uploader = YouTubeUploader()
    
    # Test authentication
    try:
        service = uploader._get_service()
        print("✅ Authentication successful")
        
        # Show upload settings
        settings = uploader.default_settings
        print(f"\n⚙️ Default Upload Settings:")
        print(f"   Privacy: {settings['privacy_status']}")
        print(f"   Category: {settings['category_id']}")
        print(f"   Language: {settings['language']}")
        print(f"   Default Tags: {settings['default_tags']}")
        
        # Show quota costs
        print(f"\n📊 Quota Costs:")
        print(f"   Video Upload: 1,600 units")
        print(f"   Thumbnail Upload: 50 units")
        print(f"   Total (with thumbnail): {uploader.get_upload_quota_cost(True)} units")
        
        print(f"\n💡 Ready for video uploads!")
        print(f"   Create test video: tests/create_test_video.py")
        print(f"   Upload test: tests/test_upload.py")
        
    except Exception as e:
        print(f"❌ Setup incomplete: {e}")
        print("\nSetup required:")
        print("1. Complete OAuth authentication: python auth/youtube_auth.py")
        print("2. Download client_secrets.json to auth/ directory")

if __name__ == "__main__":
    main()