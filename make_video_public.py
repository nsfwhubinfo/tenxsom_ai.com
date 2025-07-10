#!/usr/bin/env python3
"""
Make the test video public to verify channel visibility
"""

import sys
sys.path.append("youtube-upload-pipeline")
from services.multi_channel_token_manager import get_token_manager

def make_test_video_public():
    """Make the uploaded test video public"""
    print("🎬 MAKING TEST VIDEO PUBLIC")
    print("=" * 40)
    
    try:
        manager = get_token_manager()
        youtube, channel_info = manager.get_channel_service("hub")
        
        # Get the uploaded video
        video_id = "wrz_IBzKAq0"  # From our previous upload
        
        print(f"📹 Video ID: {video_id}")
        print(f"📺 Channel: {channel_info['channel_name']}")
        
        # Update video privacy to public
        update_request = youtube.videos().update(
            part="status",
            body={
                "id": video_id,
                "status": {
                    "privacyStatus": "public",
                    "selfDeclaredMadeForKids": False
                }
            }
        )
        
        response = update_request.execute()
        
        if response:
            print("✅ Video successfully made public!")
            print(f"🌐 URL: https://www.youtube.com/watch?v={video_id}")
            print("🎉 Video should now be visible on your channel!")
            
            # Get updated channel stats
            channel_response = youtube.channels().list(
                part="statistics",
                mine=True
            ).execute()
            
            if channel_response["items"]:
                stats = channel_response["items"][0]["statistics"]
                print(f"\n📊 Updated Channel Stats:")
                print(f"   Public Videos: {stats.get('videoCount', '0')}")
                print(f"   Total Views: {stats.get('viewCount', '0')}")
            
            return True
        else:
            print("❌ Failed to update video privacy")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = make_test_video_public()
    if success:
        print("\n🎉 SUCCESS! Your TenxsomAI channel now has a public video!")
    else:
        print("\n❌ Failed to make video public")