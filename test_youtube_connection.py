#!/usr/bin/env python3
"""
Quick test of YouTube OAuth authentication
"""

import sys
sys.path.append("youtube-upload-pipeline")

from services.multi_channel_token_manager import get_token_manager

def test_hub_channel():
    """Test hub channel authentication"""
    try:
        manager = get_token_manager()
        
        # Check channel status
        channels = manager.list_available_channels()
        print("\n📺 Channel Status:")
        for key, info in channels.items():
            status = "✅" if info["ready"] else "❌"
            print(f"   {status} {info['name']} ({info['role']})")
        
        # Test hub channel
        if channels["hub"]["ready"]:
            print("\n🔐 Testing hub channel connection...")
            youtube, channel_info = manager.get_channel_service("hub")
            
            # Get channel details
            response = youtube.channels().list(
                part="snippet,statistics",
                mine=True
            ).execute()
            
            if response["items"]:
                channel = response["items"][0]
                print(f"\n✅ Connected to: {channel['snippet']['title']}")
                print(f"   Subscribers: {channel['statistics'].get('subscriberCount', 'Hidden')}")
                print(f"   Total videos: {channel['statistics'].get('videoCount', '0')}")
                print(f"   Total views: {channel['statistics'].get('viewCount', '0')}")
                
                return True
        else:
            print("\n❌ Hub channel not authenticated yet")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_hub_channel()
    sys.exit(0 if success else 1)
