#!/usr/bin/env python3

"""
Tenxsom AI Chatbot Setup Script
Configures and deploys the complete chatbot system
"""

import asyncio
import os
import sys
from pathlib import Path
import subprocess
import json

def print_header(title: str):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"🤖 {title}")
    print("="*60)

def print_step(step: str):
    """Print step with formatting"""
    print(f"\n📋 {step}...")

def print_success(message: str):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message"""
    print(f"❌ {message}")

def print_warning(message: str):
    """Print warning message"""
    print(f"⚠️ {message}")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print_error("Python 3.8+ is required")
        sys.exit(1)
    print_success(f"Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_requirements():
    """Install required packages"""
    print_step("Installing Python dependencies")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, capture_output=True)
        print_success("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to install dependencies: {e}")
        print("📝 You can install manually with:")
        print(f"   pip install -r {requirements_file}")
        return False
    
    return True

def setup_environment():
    """Set up environment configuration"""
    print_step("Setting up environment configuration")
    
    env_file = Path(__file__).parent / ".env"
    
    # Check if .env already exists
    if env_file.exists():
        print_warning(".env file already exists")
        return True
    
    # Create .env template
    env_template = """# Tenxsom AI Chatbot Configuration

# UseAPI.net Configuration
USEAPI_BEARER_TOKEN=user:1831-r8vA1WGayarXKuYwpT1PW

# Telegram Bot Configuration (Get from @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
AUTHORIZED_USER_ID=your_telegram_user_id_here

# Optional: Advanced Configuration
LOG_LEVEL=INFO
MAX_CONVERSATION_HISTORY=50
ENABLE_VECTOR_SEARCH=false

# Optional: MiniMax API (for enhanced LLM capabilities)
MINIMAX_API_KEY=your_minimax_api_key_here
MINIMAX_API_HOST=https://api.minimax.io
"""
    
    with open(env_file, 'w') as f:
        f.write(env_template)
    
    print_success("Environment template created")
    print("📝 Please edit .env file with your actual tokens:")
    print(f"   {env_file}")
    
    return True

def create_telegram_bot():
    """Guide user through Telegram bot creation"""
    print_step("Telegram Bot Setup Guide")
    
    print("""
🤖 To create a Telegram bot:

1. Open Telegram and search for @BotFather
2. Send /newbot command
3. Choose a name: "Tenxsom AI Assistant"
4. Choose a username: "your_username_tenxsom_bot"
5. Copy the bot token you receive
6. Add the token to your .env file

📱 To find your Telegram user ID:
1. Search for @userinfobot on Telegram
2. Send /start to get your user ID
3. Add your user ID to .env file

This ensures only you can use the bot!
""")

def test_documentation_server():
    """Test the documentation server"""
    print_step("Testing Documentation MCP Server")
    
    try:
        # Import and test the documentation server
        sys.path.append(str(Path(__file__).parent))
        from mcp_servers.documentation_server import TechnicalReportsMCP
        
        async def run_test():
            server = TechnicalReportsMCP()
            result = await server.execute_tool(
                "query_technical_docs",
                {"query": "HeyGen TTS setup"}
            )
            return result.get("status") == "success"
        
        success = asyncio.run(run_test())
        
        if success:
            print_success("Documentation server working correctly")
        else:
            print_warning("Documentation server test failed")
            
    except Exception as e:
        print_warning(f"Documentation server test error: {e}")

def create_systemd_service():
    """Create systemd service for production deployment"""
    print_step("Creating systemd service (optional)")
    
    service_content = f"""[Unit]
Description=Tenxsom AI Chatbot
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'root')}
WorkingDirectory={Path(__file__).parent}
Environment=PATH={os.environ['PATH']}
ExecStart={sys.executable} central-controller.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    service_file = Path(__file__).parent / "tenxsom-chatbot.service"
    
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    print_success("Systemd service file created")
    print("📝 To install as system service:")
    print(f"   sudo cp {service_file} /etc/systemd/system/")
    print("   sudo systemctl enable tenxsom-chatbot")
    print("   sudo systemctl start tenxsom-chatbot")

def create_startup_script():
    """Create startup script"""
    print_step("Creating startup script")
    
    startup_script = Path(__file__).parent / "start-chatbot.sh"
    
    script_content = f"""#!/bin/bash

# Tenxsom AI Chatbot Startup Script

echo "🤖 Starting Tenxsom AI Chatbot..."

# Change to chatbot directory
cd "{Path(__file__).parent}"

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if bot token is configured
if [ -z "$TELEGRAM_BOT_TOKEN" ] || [ "$TELEGRAM_BOT_TOKEN" = "your_telegram_bot_token_here" ]; then
    echo "❌ Please configure TELEGRAM_BOT_TOKEN in .env file"
    exit 1
fi

# Start the chatbot
{sys.executable} central-controller.py
"""
    
    with open(startup_script, 'w') as f:
        f.write(script_content)
    
    # Make executable
    startup_script.chmod(0o755)
    
    print_success("Startup script created")
    print(f"📝 Run with: {startup_script}")

def create_config_file():
    """Create main configuration file"""
    print_step("Creating configuration file")
    
    config = {
        "chatbot": {
            "name": "Tenxsom AI Assistant",
            "version": "1.0.0",
            "personality": "Direct service operator and technical expert",
            "max_context_length": 32000,
            "response_timeout": 30
        },
        "services": {
            "useapi": {
                "base_url": "https://api.useapi.net/v1",
                "services": ["ltx_studio", "heygen", "midjourney", "kling"],
                "rate_limit": 60
            },
            "telegram": {
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
                "timeout": 30
            }
        },
        "mcp_servers": [
            {
                "name": "documentation",
                "path": "./mcp-servers/documentation-server.py",
                "tools": [
                    "query_technical_docs",
                    "search_troubleshooting", 
                    "get_config_examples",
                    "find_error_solutions"
                ]
            },
            {
                "name": "useapi",
                "path": "../useapi-mcp-server/src/useapi_mcp_server/server.py",
                "tools": [
                    "ltx_studio_video_create",
                    "heygen_tts_generate",
                    "midjourney_imagine"
                ]
            }
        ],
        "logging": {
            "level": "INFO",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "file": "chatbot.log"
        }
    }
    
    config_file = Path(__file__).parent / "config.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print_success("Configuration file created")

def main():
    """Main setup function"""
    print_header("Tenxsom AI Chatbot Setup")
    
    print("""
🎯 This script will set up your complete chatbot system including:

• 🤖 Central chatbot controller with UseAPI.net Minimax LLM
• 📱 Telegram bot interface for mobile control
• 📚 Documentation MCP server for technical reports
• ⚙️ System configuration and startup scripts
• 🔧 Production deployment options

Let's get started!
""")
    
    # Step 1: Check Python version
    print_step("Checking Python version")
    check_python_version()
    
    # Step 2: Install dependencies
    if not install_requirements():
        print_error("Setup failed - please install dependencies manually")
        return
    
    # Step 3: Set up environment
    setup_environment()
    
    # Step 4: Create configuration
    create_config_file()
    
    # Step 5: Test documentation server
    test_documentation_server()
    
    # Step 6: Create startup script
    create_startup_script()
    
    # Step 7: Create systemd service
    create_systemd_service()
    
    # Step 8: Telegram bot setup guide
    create_telegram_bot()
    
    print_header("Setup Complete!")
    
    print("""
🎉 Tenxsom AI Chatbot setup is complete!

📋 Next Steps:

1. **Configure Telegram Bot**:
   • Create bot with @BotFather
   • Add bot token to .env file
   • Add your user ID to .env file

2. **Test the System**:
   • Run: ./start-chatbot.sh
   • Or: python central-controller.py

3. **Production Deployment**:
   • Install systemd service (see instructions above)
   • Configure firewall if needed
   • Set up monitoring and logging

🚀 **Key Features Ready**:
• 💬 Natural language system control
• 📱 Mobile access via Telegram
• 📚 Instant access to all technical documentation
• 🎬 Content generation with HeyGen TTS
• ⚙️ Complete system management

💡 **Example Commands to Try**:
• "Generate 3 YouTube videos about AI trends"
• "Check system status and account limits"
• "How do I fix 522 timeout errors?"
• "Create narration for this script: [your text]"

Happy chatbotting! 🤖✨
""")

if __name__ == "__main__":
    main()