#!/usr/bin/env python3

"""
Setup script for UseAPI MCP Server development
"""

import subprocess
import sys
import os


def run_command(command, description):
    """Run a command and print the result"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("🚀 Setting up UseAPI MCP Server Development Environment")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install in development mode
    if not run_command("pip install -e .", "Installing package in development mode"):
        sys.exit(1)
    
    # Install development dependencies
    if not run_command("pip install pytest pytest-asyncio black mypy ruff", "Installing development dependencies"):
        print("⚠️  Development dependencies failed, but package should still work")
    
    # Try to install MCP dependencies
    if not run_command("pip install mcp httpx asyncio-throttle", "Installing MCP dependencies"):
        print("⚠️  Some dependencies failed - you may need to install them manually")
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Set your UseAPI.net API key:")
    print("   export USEAPI_API_KEY='your-api-key-here'")
    print("\n2. Test the server:")
    print("   python -m useapi_mcp_server")
    print("\n3. Add to Claude Desktop config:")
    print("   See examples/claude_desktop_config.json")
    print("\n4. Run tests:")
    print("   pytest tests/")
    print("\n📚 Documentation: README.md")


if __name__ == "__main__":
    main()