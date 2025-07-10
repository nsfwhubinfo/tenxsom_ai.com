#!/usr/bin/env python3
"""
Set up Telegram webhook for TenxsomAI bot
"""
import requests
import json
import sys

# Bot configuration
BOT_TOKEN = "8165715351:AAGx8GbvklCMy0o7B2Kuo6wz8_aKcvBcMO8"
WEBHOOK_URL = "https://tenxsom-video-worker-hpkm6siuqq-uc.a.run.app/telegram/webhook"

def get_webhook_info():
    """Get current webhook configuration"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"
    response = requests.get(url)
    return response.json()

def set_webhook():
    """Set webhook URL for the bot"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {
        "url": WEBHOOK_URL,
        "allowed_updates": ["message", "callback_query"],
        "drop_pending_updates": False
    }
    response = requests.post(url, json=data)
    return response.json()

def delete_webhook():
    """Delete webhook (revert to polling)"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    response = requests.post(url)
    return response.json()

def main():
    print("Telegram Webhook Setup")
    print("=" * 50)
    
    # Check current webhook status
    print("\nCurrent webhook status:")
    info = get_webhook_info()
    print(json.dumps(info, indent=2))
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "delete":
            print("\nDeleting webhook...")
            result = delete_webhook()
            print(json.dumps(result, indent=2))
            return
    
    # Set new webhook
    print(f"\nSetting webhook to: {WEBHOOK_URL}")
    result = set_webhook()
    print(json.dumps(result, indent=2))
    
    if result.get("ok"):
        print("\n✅ Webhook successfully configured!")
        # Verify setup
        print("\nVerifying webhook configuration:")
        info = get_webhook_info()
        print(json.dumps(info, indent=2))
    else:
        print("\n❌ Failed to set webhook")
        print(f"Error: {result.get('description')}")

if __name__ == "__main__":
    main()