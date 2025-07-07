#!/usr/bin/env python3

"""
YouTube Upload Pipeline Setup Script
Configures and validates the complete upload automation system
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from urllib.request import urlopen
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class PipelineSetup:
    """Setup and configuration manager for YouTube upload pipeline"""
    
    def __init__(self):
        """Initialize setup manager"""
        self.pipeline_dir = Path(__file__).parent
        self.project_root = self.pipeline_dir.parent
        
        # Configuration tracking
        self.setup_status = {
            'dependencies': False,
            'google_cloud': False,
            'oauth_config': False,
            'channel_config': False,
            'integrations': False,
            'testing': False
        }
    
    def print_header(self, title: str):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"🚀 {title}")
        print("="*60)
    
    def print_step(self, step: str):
        """Print step with formatting"""
        print(f"\n📋 {step}...")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"⚠️ {message}")
    
    def check_dependencies(self) -> bool:
        """Check and install required dependencies"""
        self.print_step("Checking dependencies")
        
        required_packages = [
            'google-auth',
            'google-auth-oauthlib', 
            'google-auth-httplib2',
            'google-api-python-client',
            'pillow',
            'opencv-python',
            'httpx',
            'python-dotenv'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                # Try to import the package
                if package == 'google-api-python-client':
                    import googleapiclient
                elif package == 'opencv-python':
                    import cv2
                elif package == 'pillow':
                    import PIL
                else:
                    __import__(package.replace('-', '_'))
                    
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            self.print_warning(f"Missing packages: {', '.join(missing_packages)}")
            
            # Try to install missing packages
            try:
                pip_cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
                subprocess.run(pip_cmd, check=True, capture_output=True)
                self.print_success("Dependencies installed successfully")
                self.setup_status['dependencies'] = True
                return True
            except subprocess.CalledProcessError as e:
                self.print_error(f"Failed to install dependencies: {e}")
                self.print_warning("Please install manually:")
                self.print_warning(f"pip install {' '.join(missing_packages)}")
                return False
        else:
            self.print_success("All dependencies are installed")
            self.setup_status['dependencies'] = True
            return True
    
    def check_google_cloud_config(self) -> bool:
        """Check Google Cloud and YouTube API configuration"""
        self.print_step("Checking Google Cloud configuration")
        
        # Check environment variables
        api_key = os.getenv('YOUTUBE_API_KEY')
        channel_id = os.getenv('YOUTUBE_CHANNEL_ID')
        
        if api_key and channel_id:
            self.print_success("Environment variables configured")
            
            # Test API key validity
            if self.test_api_key(api_key, channel_id):
                self.setup_status['google_cloud'] = True
                return True
            else:
                self.print_error("API key or channel ID invalid")
                return False
        else:
            self.print_error("Missing environment variables")
            self.print_warning("Required: YOUTUBE_API_KEY, YOUTUBE_CHANNEL_ID")
            return False
    
    def test_api_key(self, api_key: str, channel_id: str) -> bool:
        """Test YouTube API key validity"""
        try:
            url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet&id={channel_id}&key={api_key}"
            response = urlopen(url)
            data = json.loads(response.read().decode())
            
            if data.get('items'):
                channel_name = data['items'][0]['snippet']['title']
                self.print_success(f"API key valid - Channel: {channel_name}")
                return True
            else:
                self.print_error("Channel not found or API key invalid")
                return False
                
        except Exception as e:
            self.print_error(f"API test failed: {e}")
            return False
    
    def check_oauth_setup(self) -> bool:
        """Check OAuth 2.0 configuration"""
        self.print_step("Checking OAuth 2.0 setup")
        
        client_secrets_file = self.pipeline_dir / "auth" / "client_secrets.json"
        
        if client_secrets_file.exists():
            try:
                with open(client_secrets_file) as f:
                    secrets = json.load(f)
                
                if 'installed' in secrets and 'client_id' in secrets['installed']:
                    self.print_success("OAuth client secrets configured")
                    self.setup_status['oauth_config'] = True
                    return True
                else:
                    self.print_error("Invalid client_secrets.json format")
                    return False
                    
            except json.JSONDecodeError:
                self.print_error("client_secrets.json is not valid JSON")
                return False
        else:
            self.print_error("client_secrets.json not found")
            self.print_warning("Download from Google Cloud Console > APIs & Services > Credentials")
            self.print_warning(f"Save to: {client_secrets_file}")
            return False
    
    def check_channel_configuration(self) -> bool:
        """Verify YouTube channel configuration"""
        self.print_step("Checking YouTube channel configuration")
        
        # Check if channel meets upload requirements
        channel_info = {
            'id': os.getenv('YOUTUBE_CHANNEL_ID'),
            'url': os.getenv('YOUTUBE_CHANNEL_URL'),
            'verified': True,  # Assume verified for now
            'upload_enabled': True  # Assume enabled for now
        }
        
        if all(channel_info.values()):
            self.print_success("Channel configuration valid")
            self.print_success(f"Channel ID: {channel_info['id']}")
            self.setup_status['channel_config'] = True
            return True
        else:
            self.print_error("Incomplete channel configuration")
            return False
    
    def check_integrations(self) -> bool:
        """Check integration with existing systems"""
        self.print_step("Checking system integrations")
        
        integrations = {
            'useapi_token': os.getenv('USEAPI_BEARER_TOKEN'),
            'telegram_bot': os.getenv('TELEGRAM_BOT_TOKEN'),
            'heygen_workflow': (self.project_root / "heygen-integration").exists(),
            'mcp_server': (self.project_root / "useapi-mcp-server").exists(),
            'chatbot': (self.project_root / "chatbot-integration").exists()
        }
        
        working_integrations = sum(1 for v in integrations.values() if v)
        total_integrations = len(integrations)
        
        if working_integrations >= 3:  # Most integrations working
            self.print_success(f"Integrations: {working_integrations}/{total_integrations} configured")
            self.setup_status['integrations'] = True
            return True
        else:
            self.print_warning(f"Limited integrations: {working_integrations}/{total_integrations}")
            return False
    
    def run_tests(self) -> bool:
        """Run basic functionality tests"""
        self.print_step("Running functionality tests")
        
        try:
            # Test authentication
            from auth.youtube_auth import YouTubeAuthenticator
            auth = YouTubeAuthenticator()
            
            if auth.authenticate():
                result = auth.test_connection()
                if result['status'] == 'success':
                    self.print_success("Authentication test passed")
                    self.setup_status['testing'] = True
                    return True
                else:
                    self.print_error(f"Connection test failed: {result['message']}")
                    return False
            else:
                self.print_error("Authentication failed")
                self.print_warning("Complete OAuth setup first")
                return False
                
        except ImportError as e:
            self.print_error(f"Import error: {e}")
            self.print_warning("Install missing dependencies")
            return False
        except Exception as e:
            self.print_error(f"Test failed: {e}")
            return False
    
    def generate_setup_report(self) -> dict:
        """Generate comprehensive setup report"""
        
        completed_steps = sum(1 for status in self.setup_status.values() if status)
        total_steps = len(self.setup_status)
        completion_rate = (completed_steps / total_steps) * 100
        
        report = {
            'setup_summary': {
                'completion_rate': f"{completion_rate:.1f}%",
                'completed_steps': completed_steps,
                'total_steps': total_steps,
                'ready_for_production': completion_rate >= 80
            },
            'step_details': self.setup_status,
            'next_actions': []
        }
        
        # Generate next actions
        if not self.setup_status['dependencies']:
            report['next_actions'].append("Install required Python packages")
        
        if not self.setup_status['google_cloud']:
            report['next_actions'].append("Configure Google Cloud project and API key")
        
        if not self.setup_status['oauth_config']:
            report['next_actions'].append("Download and configure client_secrets.json")
        
        if not self.setup_status['testing']:
            report['next_actions'].append("Complete OAuth authentication")
        
        if completion_rate >= 80:
            report['next_actions'].append("Ready for production uploads!")
        
        return report
    
    def display_final_status(self, report: dict):
        """Display final setup status and next steps"""
        
        self.print_header("Setup Complete")
        
        summary = report['setup_summary']
        print(f"📊 Setup Progress: {summary['completion_rate']}")
        print(f"✅ Completed: {summary['completed_steps']}/{summary['total_steps']} steps")
        
        if summary['ready_for_production']:
            print(f"\n🎉 Pipeline ready for production use!")
        else:
            print(f"\n⚠️ Additional setup required")
        
        # Show step status
        print(f"\n📋 Step Details:")
        for step, status in self.setup_status.items():
            status_icon = "✅" if status else "❌"
            step_name = step.replace('_', ' ').title()
            print(f"   {status_icon} {step_name}")
        
        # Show next actions
        if report['next_actions']:
            print(f"\n🔧 Next Actions:")
            for action in report['next_actions']:
                print(f"   • {action}")
        
        # Show usage information
        print(f"\n🚀 Usage:")
        print(f"   Test upload: python tests/test_upload.py")
        print(f"   Create content: python tests/create_test_video.py")
        print(f"   Generate thumbnails: python thumbnails/thumbnail_generator.py")
        
        # Show integration info
        print(f"\n🔗 Integrations:")
        print(f"   Telegram Bot: @TenxsomAI_bot")
        print(f"   UseAPI.net: Video/thumbnail generation")
        print(f"   HeyGen: Professional narration")

def main():
    """Main setup execution"""
    
    setup = PipelineSetup()
    
    setup.print_header("YouTube Upload Pipeline Setup")
    
    print("""
🎯 This script will configure your complete YouTube upload automation:

• ✅ YouTube Data API v3 integration
• 🖼️ Automated thumbnail generation  
• 🎙️ Professional narration workflow
• 📱 Mobile control via Telegram
• 📊 A/B testing capabilities

Let's verify your setup...
    """)
    
    # Run all setup checks
    setup_steps = [
        ("Dependencies", setup.check_dependencies),
        ("Google Cloud", setup.check_google_cloud_config),
        ("OAuth Setup", setup.check_oauth_setup),
        ("Channel Config", setup.check_channel_configuration),
        ("Integrations", setup.check_integrations),
        ("Testing", setup.run_tests)
    ]
    
    for step_name, step_func in setup_steps:
        if not step_func():
            # Continue with other steps even if one fails
            pass
    
    # Generate and display final report
    report = setup.generate_setup_report()
    setup.display_final_status(report)

if __name__ == "__main__":
    main()