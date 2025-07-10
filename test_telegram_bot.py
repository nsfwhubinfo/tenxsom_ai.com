#!/usr/bin/env python3
"""
Test Telegram bot connectivity and functionality
"""

import asyncio
import os
import json
from dotenv import load_dotenv

import httpx

# Load environment variables
load_dotenv()

async def test_telegram_bot():
    """Test Telegram bot connectivity"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ No TELEGRAM_BOT_TOKEN found in environment")
        return False
    
    print("🤖 Testing Telegram Bot...")
    print(f"Bot Token: {bot_token[:20]}...")
    
    try:
        async with httpx.AsyncClient() as client:
            # Test getMe endpoint
            response = await client.get(f"https://api.telegram.org/bot{bot_token}/getMe")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("ok"):
                    bot_info = data.get("result", {})
                    print(f"✅ Bot Connected: @{bot_info.get('username', 'unknown')}")
                    print(f"   Bot Name: {bot_info.get('first_name', 'Unknown')}")
                    print(f"   Bot ID: {bot_info.get('id', 'Unknown')}")
                    
                    # Test getUpdates to see if bot is receiving messages
                    updates_response = await client.get(f"https://api.telegram.org/bot{bot_token}/getUpdates")
                    if updates_response.status_code == 200:
                        updates_data = updates_response.json()
                        update_count = len(updates_data.get("result", []))
                        print(f"   Pending Updates: {update_count}")
                    
                    return True
                else:
                    print(f"❌ Bot API Error: {data.get('description', 'Unknown error')}")
                    return False
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

async def main():
    """Main test runner"""
    success = await test_telegram_bot()
    
    if success:
        print("\n✅ Telegram bot is properly configured and accessible!")
        print("   You can start the bot with: cd chatbot-integration && python3 central-controller.py")
    else:
        print("\n❌ Telegram bot test failed. Please check your bot token.")

if __name__ == "__main__":
    asyncio.run(main())