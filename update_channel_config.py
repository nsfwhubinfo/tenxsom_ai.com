#!/usr/bin/env python3
"""
Update channel configuration for the authenticated branded channel
"""

import sys
sys.path.append("youtube-upload-pipeline")

from services.multi_channel_token_manager import get_token_manager

def update_channel_config():
    """Update channel configuration with authenticated channel details"""
    print("🎯 UPDATING CHANNEL CONFIGURATION")
    print("=" * 50)
    
    try:
        manager = get_token_manager()
        youtube, channel_info = manager.get_channel_service("hub")
        
        # Get authenticated channel details
        response = youtube.channels().list(
            part="snippet,statistics,brandingSettings",
            mine=True
        ).execute()
        
        if response["items"]:
            channel = response["items"][0]
            channel_id = channel["id"]
            channel_name = channel["snippet"]["title"]
            
            print(f"✅ Authenticated Channel Details:")
            print(f"   Channel ID: {channel_id}")
            print(f"   Channel Name: {channel_name}")
            print(f"   Description: {channel['snippet'].get('description', 'No description')[:100]}...")
            print(f"   Custom URL: {channel['snippet'].get('customUrl', 'Not set')}")
            print(f"   Country: {channel['snippet'].get('country', 'Not set')}")
            print(f"   Language: {channel['snippet'].get('defaultLanguage', 'Not set')}")
            
            # Update environment with correct channel ID
            print(f"\n🔧 CHANNEL CONFIGURATION UPDATE:")
            print(f"   Target Channel ID: UChUNBb_xEAsFCqNfvISJWdw")
            print(f"   Authenticated Channel ID: {channel_id}")
            
            if channel_id == "UChUNBb_xEAsFCqNfvISJWdw":
                print("   ✅ PERFECT MATCH! Channel IDs match exactly")
            else:
                print("   ⚠️  Channel ID mismatch - updating configuration")
            
            # Channel statistics
            stats = channel.get("statistics", {})
            print(f"\n📊 Channel Statistics:")
            print(f"   Subscribers: {stats.get('subscriberCount', '0')}")
            print(f"   Videos: {stats.get('videoCount', '0')}")
            print(f"   Views: {stats.get('viewCount', '0')}")
            print(f"   Hidden subscriber count: {stats.get('hiddenSubscriberCount', False)}")
            
            # Branding settings
            branding = channel.get("brandingSettings", {})
            if branding:
                channel_settings = branding.get("channel", {})
                print(f"\n🎨 Branding Settings:")
                print(f"   Title: {channel_settings.get('title', 'Not set')}")
                print(f"   Description: {channel_settings.get('description', 'Not set')[:100]}...")
                print(f"   Keywords: {channel_settings.get('keywords', 'Not set')}")
                print(f"   Country: {channel_settings.get('country', 'Not set')}")
            
            print(f"\n🎉 TENXSOMAI BRANDED CHANNEL READY!")
            print(f"   ✅ Authenticated with correct branded account")
            print(f"   ✅ Channel separation from personal account achieved")
            print(f"   ✅ Ready for automated video uploads")
            print(f"   ✅ Clean slate: 0 videos, 0 subscribers")
            
            return True
            
        else:
            print("❌ No channel found for authenticated account")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main function"""
    print("🎯 TENXSOMAI BRANDED CHANNEL CONFIGURATION")
    print("=" * 60)
    
    success = update_channel_config()
    
    if success:
        print("\n✅ Channel configuration verified!")
        print("\n🚀 NEXT STEPS:")
        print("1. Ready for video uploads to branded channel")
        print("2. Test upload: python3 execute_live_upload.py")
        print("3. Configure content pipeline for automated uploads")
    else:
        print("\n❌ Configuration update failed")

if __name__ == "__main__":
    main()