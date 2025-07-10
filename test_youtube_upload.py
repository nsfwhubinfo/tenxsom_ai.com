#!/usr/bin/env python3
"""
Test YouTube upload functionality with a sample video
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add paths to import modules
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "youtube-upload-pipeline"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class YouTubeUploadTester:
    """Test YouTube upload functionality"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "success": False
        }
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        print("🔍 Checking prerequisites...")
        
        checks = {
            "YouTube API Key": os.getenv("YOUTUBE_API_KEY"),
            "YouTube Channel ID": os.getenv("YOUTUBE_CHANNEL_ID"),
            "Client Secrets File": os.path.exists("youtube-upload-pipeline/auth/client_secrets.json"),
            "YouTube Service Module": os.path.exists("youtube-upload-pipeline/services/youtube_uploader.py")
        }
        
        all_passed = True
        for check_name, check_result in checks.items():
            if check_result:
                print(f"✅ {check_name}: OK")
            else:
                print(f"❌ {check_name}: FAILED")
                all_passed = False
        
        return all_passed
    
    async def create_test_video(self) -> str:
        """Create a simple test video file"""
        print("\n🎥 Creating test video...")
        
        # Create a simple test video using ffmpeg
        test_video_path = "videos/output/test_upload_video.mp4"
        os.makedirs("videos/output", exist_ok=True)
        
        # Create a 5-second test video with text overlay
        ffmpeg_command = f"""
        ffmpeg -y -f lavfi -i color=c=blue:s=1280x720:d=5 \
        -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:\
        text='TenxsomAI Test Upload\\n{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}':fontcolor=white:fontsize=48:\
        box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=(h-text_h)/2" \
        -c:v libx264 -t 5 {test_video_path} 2>/dev/null
        """
        
        result = os.system(ffmpeg_command)
        
        if result == 0 and os.path.exists(test_video_path):
            file_size = os.path.getsize(test_video_path) / 1024  # KB
            print(f"✅ Test video created: {test_video_path} ({file_size:.1f} KB)")
            return test_video_path
        else:
            # Fallback: create a minimal video file for testing
            print("⚠️  ffmpeg not available, creating minimal test file...")
            with open(test_video_path, "wb") as f:
                f.write(b"FAKE_VIDEO_DATA_FOR_TESTING")  # This won't be a valid video
            return test_video_path
    
    async def test_youtube_auth(self) -> bool:
        """Test YouTube authentication"""
        print("\n🔐 Testing YouTube authentication...")
        
        try:
            from auth.youtube_auth import YouTubeAuth
            
            auth = YouTubeAuth()
            service = auth.get_authenticated_service()
            
            # Test with a simple API call
            request = service.channels().list(part="snippet", mine=True)
            response = request.execute()
            
            if "items" in response and len(response["items"]) > 0:
                channel_name = response["items"][0]["snippet"]["title"]
                print(f"✅ Authenticated as channel: {channel_name}")
                return True
            else:
                print("❌ Authentication succeeded but no channel found")
                return False
                
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            return False
    
    async def test_video_upload(self, video_path: str) -> bool:
        """Test actual video upload"""
        print("\n📤 Testing video upload...")
        
        try:
            from services.youtube_uploader import YouTubeUploader
            
            uploader = YouTubeUploader()
            
            # Prepare test metadata
            video_metadata = {
                "title": f"TenxsomAI Test Upload - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "description": "This is an automated test upload from TenxsomAI system. This video will be deleted.",
                "tags": ["test", "tenxsomai", "automated"],
                "category_id": "22",  # People & Blogs
                "privacy_status": "private"  # Keep private for testing
            }
            
            print(f"📋 Upload metadata:")
            print(f"   Title: {video_metadata['title']}")
            print(f"   Privacy: {video_metadata['privacy_status']}")
            
            # Perform upload
            video_id = uploader.upload_video(
                video_path=video_path,
                title=video_metadata["title"],
                description=video_metadata["description"],
                tags=video_metadata["tags"],
                category_id=video_metadata["category_id"],
                privacy_status=video_metadata["privacy_status"]
            )
            
            if video_id:
                print(f"✅ Video uploaded successfully!")
                print(f"   Video ID: {video_id}")
                print(f"   URL: https://youtube.com/watch?v={video_id}")
                
                self.test_results["upload_details"] = {
                    "video_id": video_id,
                    "url": f"https://youtube.com/watch?v={video_id}",
                    "metadata": video_metadata
                }
                return True
            else:
                print("❌ Upload failed - no video ID returned")
                return False
                
        except ImportError as e:
            print(f"❌ Failed to import YouTube uploader: {e}")
            print("   Attempting alternative approach...")
            return await self.test_direct_upload(video_path)
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return False
    
    async def test_direct_upload(self, video_path: str) -> bool:
        """Direct upload test without using the service module"""
        print("\n📤 Attempting direct upload test...")
        
        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            # Scopes required for YouTube upload
            SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
            
            # Check for stored credentials
            creds = None
            token_file = 'youtube-upload-pipeline/auth/token.json'
            
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            
            # If no valid credentials, initiate OAuth flow
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'youtube-upload-pipeline/auth/client_secrets.json', SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            # Build YouTube service
            youtube = build('youtube', 'v3', credentials=creds)
            
            # Prepare upload
            body = {
                'snippet': {
                    'title': f'TenxsomAI Test - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
                    'description': 'Automated test upload from TenxsomAI',
                    'tags': ['test', 'tenxsomai'],
                    'categoryId': '22'
                },
                'status': {
                    'privacyStatus': 'private'
                }
            }
            
            # Call the API's videos.insert method
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
            )
            
            response = insert_request.execute()
            
            if 'id' in response:
                video_id = response['id']
                print(f"✅ Direct upload successful!")
                print(f"   Video ID: {video_id}")
                print(f"   URL: https://youtube.com/watch?v={video_id}")
                return True
            else:
                print("❌ Upload response missing video ID")
                return False
                
        except Exception as e:
            print(f"❌ Direct upload failed: {e}")
            return False
    
    async def run_test(self):
        """Run the complete YouTube upload test"""
        print("🚀 YOUTUBE UPLOAD TEST")
        print("=" * 50)
        
        # Check prerequisites
        if not self.check_prerequisites():
            print("\n❌ Prerequisites check failed. Please ensure all required files and credentials are in place.")
            return False
        
        # Create test video
        video_path = await self.create_test_video()
        if not video_path or not os.path.exists(video_path):
            print("\n❌ Failed to create test video")
            return False
        
        # Test authentication
        auth_success = await self.test_youtube_auth()
        self.test_results["tests"].append({
            "name": "YouTube Authentication",
            "success": auth_success
        })
        
        if not auth_success:
            print("\n⚠️  Authentication test failed, but continuing with upload test...")
        
        # Test upload
        upload_success = await self.test_video_upload(video_path)
        self.test_results["tests"].append({
            "name": "Video Upload",
            "success": upload_success
        })
        
        # Clean up test video
        try:
            os.remove(video_path)
            print(f"\n🧹 Cleaned up test video: {video_path}")
        except:
            pass
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        all_passed = all(test["success"] for test in self.test_results["tests"])
        self.test_results["success"] = all_passed
        
        for test in self.test_results["tests"]:
            status = "✅ PASSED" if test["success"] else "❌ FAILED"
            print(f"{test['name']}: {status}")
        
        # Save results
        with open("youtube_upload_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📄 Results saved to: youtube_upload_test_results.json")
        
        if all_passed:
            print("\n🎉 YouTube upload test PASSED! System is ready for production uploads.")
            if "upload_details" in self.test_results:
                print(f"\n📺 Test video uploaded (private): {self.test_results['upload_details']['url']}")
                print("   Note: This is a private video for testing purposes.")
        else:
            print("\n⚠️  YouTube upload test had some failures. Please check the logs.")
        
        return all_passed


async def main():
    """Main test runner"""
    tester = YouTubeUploadTester()
    success = await tester.run_test()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())