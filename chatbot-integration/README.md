# 🤖 Tenxsom AI Chatbot

## ✅ Current Setup Status

- **Bot Name**: @TenxsomAI_bot
- **User ID**: 8088003389 (configured)
- **Bot Token**: Needs to be added from @BotFather

## 🚀 Quick Start

### 1. **Add Your Bot Token**

Edit the `.env` file and replace `YOUR_BOT_TOKEN_FROM_BOTFATHER` with your actual bot token:

```bash
nano .env
```

The token should look like: `1234567890:ABCdefGHIjklMNOpqrSTUvwxyz`

### 2. **Install Dependencies**

```bash
pip3 install -r requirements.txt
```

Or run the setup script:

```bash
python3 setup-chatbot.py
```

### 3. **Start the Chatbot**

```bash
# Option 1: Direct start
python3 central-controller.py

# Option 2: Using startup script (if created)
./start-chatbot.sh
```

### 4. **Test on Telegram**

1. Open Telegram and find **@TenxsomAI_bot**
2. Send `/start` to initialize
3. Try these commands:
   - `/status` - Check system status
   - `/help` - Show available commands

## 💬 Example Commands

### Natural Language Examples:
- "Generate 3 YouTube videos about AI trends"
- "Check UseAPI.net account status"
- "How do I fix 522 timeout errors?"
- "Create narration for this script: [your text]"
- "Show me the video generation workflow"

### System Management:
- "Deploy new configuration"
- "Check system health"
- "Scale up accounts for more capacity"
- "Backup current system state"

## 📱 Features

- **Mobile Control**: Full system access from your phone
- **Documentation Search**: Instant access to 13 technical documents
- **Content Generation**: Videos, images, narration with HeyGen TTS
- **System Management**: Monitor and control all services
- **Natural Language**: No need to remember complex commands

## 🔒 Security

- Only User ID `8088003389` can access the bot
- Bot token stored securely in `.env` file
- All other users receive "Unauthorized access" message

## 📊 Available MCP Servers

1. **Documentation Server**: Query technical reports and guides
2. **UseAPI.net Server**: Access all AI generation services
3. **System Control**: Manage configuration and deployment

## 🛠️ Troubleshooting

### Bot doesn't respond:
1. Check bot token is correct in `.env`
2. Verify `python3 central-controller.py` is running
3. Look for errors in console output

### "Unauthorized" error:
- Your User ID (8088003389) is already configured correctly
- This error appears for other users (security feature)

### Connection issues:
- Ensure internet connection is stable
- Check UseAPI.net service status
- Review logs for specific errors

## 📁 Project Structure

```
chatbot-integration/
├── central-controller.py      # Main chatbot controller
├── mcp-servers/
│   └── documentation-server.py # Technical docs MCP server
├── reference-minimax-mcp/     # MiniMax reference implementation
├── reference-telegram-mcp/    # Telegram MCP reference
├── requirements.txt          # Python dependencies
├── setup-chatbot.py         # Setup script
├── config.json             # Chatbot configuration
├── .env                    # Environment variables (add token here)
└── README.md              # This file
```

## 🎯 Next Steps

1. **Add bot token** to `.env` file
2. **Start the chatbot** with `python3 central-controller.py`
3. **Test on Telegram** with @TenxsomAI_bot
4. **Deploy to production** using systemd service (optional)

---

**Status**: Ready to launch! Just add your bot token from @BotFather.