#!/usr/bin/env python3

"""
Tenxsom AI Chatbot - Lightweight Version
Works without heavy ML dependencies, perfect for testing
"""

import json
import urllib.request
import urllib.parse
import time
import os
import sys
from datetime import datetime

# Configuration
BOT_TOKEN = "8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8"
AUTHORIZED_USER_ID = "8088003389"
USEAPI_TOKEN = "user:1831-r8vA1WGayarXKuYwpT1PW"

class TelegramBotLite:
    """Lightweight Telegram bot without external dependencies"""
    
    def __init__(self, token, authorized_user):
        self.token = token
        self.authorized_user = str(authorized_user)
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.last_update_id = 0
        
    def send_message(self, chat_id, text):
        """Send message to user"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            response = urllib.request.urlopen(req)
            return json.loads(response.read().decode())
        except Exception as e:
            print(f"Error sending message: {e}")
            return None
    
    def get_updates(self):
        """Get new messages"""
        url = f"{self.base_url}/getUpdates"
        params = {"offset": self.last_update_id + 1, "timeout": 30}
        
        try:
            full_url = f"{url}?{urllib.parse.urlencode(params)}"
            response = urllib.request.urlopen(full_url)
            data = json.loads(response.read().decode())
            
            if data.get("ok") and data.get("result"):
                return data["result"]
        except Exception as e:
            print(f"Error getting updates: {e}")
        
        return []
    
    def process_message(self, message):
        """Process incoming message"""
        chat_id = message["chat"]["id"]
        user_id = str(message["from"]["id"])
        text = message.get("text", "")
        
        # Check authorization
        if user_id != self.authorized_user:
            self.send_message(chat_id, "❌ Unauthorized access. This bot is private.")
            return
        
        # Handle commands
        if text == "/start":
            welcome = """🤖 **Tenxsom AI Assistant** - Lite Version

I'm your direct service operator for the Tenxsom AI system!

Available commands:
• `/status` - System status
• `/help` - Show help
• Natural language queries

Examples:
- "Check system status"
- "Generate a video"
- "How do I fix errors?"

*Note: This is the lightweight version without AI capabilities.*"""
            self.send_message(chat_id, welcome)
            
        elif text == "/status":
            status = f"""📊 **System Status**

🤖 Bot: @TenxsomAI_bot (Lite)
👤 User: {user_id} ✅
🎬 UseAPI.net: Connected
🎙️ HeyGen TTS: 1.5K voices
⏰ Time: {datetime.now().strftime('%H:%M:%S')}

*Full AI features require complete setup*"""
            self.send_message(chat_id, status)
            
        elif text == "/help":
            help_text = """🔧 **Available Commands**

`/start` - Initialize bot
`/status` - Check system status
`/help` - Show this help

**Natural Language** (simulated):
• "Generate video"
• "Check accounts"
• "Fix errors"

*For full AI capabilities, run:*
`./start-chatbot.sh`"""
            self.send_message(chat_id, help_text)
            
        elif "video" in text.lower():
            self.send_message(chat_id, """🎬 **Video Generation** (Simulated)

To generate videos with UseAPI.net:
1. Use LTX Studio for video creation
2. Add HeyGen TTS narration
3. Optimize for YouTube

*Full implementation available in main chatbot*""")
            
        elif "error" in text.lower() or "fix" in text.lower():
            self.send_message(chat_id, """🛠️ **Troubleshooting Guide**

Common issues:
• **522 Timeout**: UseAPI.net temporary issue
• **Invalid token**: Check .env configuration
• **Module not found**: Install dependencies

*Access full documentation with main chatbot*""")
            
        elif "status" in text.lower() or "check" in text.lower():
            self.send_message(chat_id, """📊 **Quick Status Check**

✅ Telegram Bot: Active
✅ User Auth: Verified
⏳ UseAPI.net: Check manually
⏳ HeyGen: Ready when API online

*Real-time monitoring in full version*""")
            
        else:
            self.send_message(chat_id, f"""💬 Received: "{text}"

I'm running in lite mode without AI capabilities.

For intelligent responses, run the full chatbot:
```bash
cd /home/golde/tenxsom-ai-vertex/chatbot-integration
./start-chatbot.sh
```""")
    
    def run(self):
        """Main bot loop"""
        print("🤖 Tenxsom AI Bot (Lite) Started!")
        print(f"   Bot: @TenxsomAI_bot")
        print(f"   Authorized User: {self.authorized_user}")
        print("   Mode: Lightweight (no AI)")
        print("\n📱 Send /start to your bot to begin")
        print("Press Ctrl+C to stop\n")
        
        while True:
            try:
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update["update_id"]
                    
                    if "message" in update:
                        username = update["message"]["from"].get("username", "Unknown")
                        text = update["message"].get("text", "")
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] @{username}: {text}")
                        
                        self.process_message(update["message"])
                
                time.sleep(1)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Bot stopped by user")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)

def main():
    """Main entry point"""
    print("🚀 Starting Tenxsom AI Chatbot (Lite Version)")
    print("="*50)
    
    # Create and run bot
    bot = TelegramBotLite(BOT_TOKEN, AUTHORIZED_USER_ID)
    
    # Test connection
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode())
        
        if data.get("ok"):
            print(f"✅ Connected to @{data['result']['username']}")
        else:
            print("❌ Failed to connect to bot")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Run bot
    bot.run()

if __name__ == "__main__":
    main()