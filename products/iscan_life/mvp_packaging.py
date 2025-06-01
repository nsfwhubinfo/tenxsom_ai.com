#!/usr/bin/env python3
"""
iscan.life MVP Packaging Script
================================
Packages the dashboard system as a standalone product
"""

import os
import shutil
import json
from pathlib import Path
import subprocess

class IScanLifePackager:
    """Package iscan.life for distribution"""
    
    def __init__(self):
        self.source_dir = Path("/home/golde/Tenxsom_AI")
        self.product_dir = self.source_dir / "products/iscan_life"
        self.build_dir = self.product_dir / "build"
        self.dist_dir = self.product_dir / "dist"
        
    def create_standalone_package(self):
        """Create standalone iscan.life package"""
        print("Creating iscan.life standalone package...")
        
        # Clean and create directories
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        self.build_dir.mkdir(parents=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        # Copy core files
        iscan_core = self.build_dir / "iscan_core"
        iscan_core.mkdir()
        
        # Copy dashboard components
        files_to_copy = [
            ("dashboard/executive_dashboard.py", "iscan_dashboard.py"),
            ("dashboard/knowledge_ingestion_engine.py", "iscan_ingestion.py"),
            ("dashboard/quick_note_processor.py", "iscan_notes.py"),
            ("dashboard/ocr_integration.py", "iscan_ocr.py")
        ]
        
        for src, dst in files_to_copy:
            shutil.copy2(self.source_dir / src, iscan_core / dst)
            
        # Create simplified main entry point
        self.create_main_entry()
        
        # Create setup script
        self.create_setup_script()
        
        # Create config file
        self.create_default_config()
        
        # Package as zip
        archive_name = self.dist_dir / "iscan_life_mvp_v0.1"
        shutil.make_archive(str(archive_name), 'zip', self.build_dir)
        
        print(f"✓ Package created: {archive_name}.zip")
        
    def create_main_entry(self):
        """Create main entry point for iscan.life"""
        main_content = '''#!/usr/bin/env python3
"""
iscan.life - Intelligent Scanner for Cognitive Aiding & Navigation
==================================================================
Transform scattered thoughts into structured knowledge
"""

import sys
import os
from pathlib import Path

# Add iscan_core to path
sys.path.insert(0, str(Path(__file__).parent / "iscan_core"))

from iscan_dashboard import TenxsomDashboard
from iscan_ingestion import KnowledgeIngestionEngine
from iscan_notes import QuickNoteProcessor

class IScanLife:
    """Main iscan.life application"""
    
    def __init__(self):
        self.home_dir = Path.home() / ".iscan_life"
        self.home_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.dashboard = TenxsomDashboard(str(self.home_dir))
        self.ingestion = KnowledgeIngestionEngine(str(self.home_dir))
        self.notes = QuickNoteProcessor()
        
    def run(self, command=None):
        """Run iscan.life command"""
        if not command:
            self.show_help()
        elif command == "dash":
            self.dashboard.run()
        elif command == "note":
            self.notes.quick_entry()
        elif command == "ingest":
            stats = self.ingestion.process_inbox()
            print(f"Processed: {stats}")
        elif command == "search":
            if len(sys.argv) > 2:
                query = " ".join(sys.argv[2:])
                results = self.ingestion.query_knowledge_base(query)
                for i, item in enumerate(results[:5], 1):
                    print(f"{i}. {item.source_type}: {item.content[:100]}...")
        else:
            self.show_help()
            
    def show_help(self):
        """Show help message"""
        print("""
iscan.life - Your AI-Powered Second Brain

Commands:
  iscan dash     - View executive dashboard
  iscan note     - Quick note entry
  iscan ingest   - Process inbox
  iscan search   - Search knowledge base
  
Quick Start:
  1. Add notes: iscan note
  2. Process: iscan ingest  
  3. View: iscan dash
  
Directories:
  Notes inbox: ~/.iscan_life/dashboard/knowledge_inbox/
  Processed: ~/.iscan_life/dashboard/knowledge_processed/
        """)

def main():
    app = IScanLife()
    command = sys.argv[1] if len(sys.argv) > 1 else None
    app.run(command)

if __name__ == "__main__":
    main()
'''
        
        with open(self.build_dir / "iscan", 'w') as f:
            f.write(main_content)
            
        # Make executable
        os.chmod(self.build_dir / "iscan", 0o755)
        
    def create_setup_script(self):
        """Create setup script for users"""
        setup_content = '''#!/bin/bash
# iscan.life Setup Script

echo "Setting up iscan.life..."

# Create directories
mkdir -p ~/.iscan_life/dashboard/knowledge_inbox/{notes,texts}
mkdir -p ~/.iscan_life/dashboard/knowledge_processed
mkdir -p ~/.iscan_life/dashboard/knowledge_base

# Copy files
cp -r iscan_core ~/.iscan_life/
cp iscan ~/.local/bin/ 2>/dev/null || cp iscan ~/bin/ 2>/dev/null || echo "Copy iscan to your PATH"

# Create config
cp config.json ~/.iscan_life/

echo "✓ iscan.life installed!"
echo ""
echo "Add to your PATH if needed:"
echo "  export PATH=$PATH:$PWD"
echo ""
echo "Start with: iscan"
'''
        
        with open(self.build_dir / "setup.sh", 'w') as f:
            f.write(setup_content)
            
        os.chmod(self.build_dir / "setup.sh", 0o755)
        
    def create_default_config(self):
        """Create default configuration"""
        config = {
            "version": "0.1.0",
            "settings": {
                "auto_ingest": True,
                "ocr_backend": "manual",
                "dashboard_refresh": 86400,
                "max_results": 10
            },
            "categories": [
                "general",
                "math",
                "tech", 
                "business",
                "research",
                "urgent"
            ]
        }
        
        with open(self.build_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=2)
            
    def create_landing_page(self):
        """Create simple landing page"""
        landing_html = '''<!DOCTYPE html>
<html>
<head>
    <title>iscan.life - Your AI-Powered Second Brain</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .hero {
            text-align: center;
            padding: 60px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 40px;
        }
        h1 { font-size: 3em; margin: 0; }
        .tagline { font-size: 1.5em; opacity: 0.9; }
        .cta {
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 20px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 30px;
            margin: 40px 0;
        }
        .feature {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .feature h3 { color: #667eea; }
        pre {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="hero">
        <h1>iscan.life</h1>
        <p class="tagline">Transform scattered thoughts into structured knowledge</p>
        <a href="#download" class="cta">Download Beta</a>
    </div>
    
    <h2>Never lose another brilliant idea</h2>
    <p>iscan.life uses advanced AI and mathematical pattern recognition to transform your notes, ideas, and observations into an interconnected knowledge graph.</p>
    
    <div class="features">
        <div class="feature">
            <h3>📝 Capture Everything</h3>
            <p>Quick notes, images, voice memos - capture ideas in any format</p>
        </div>
        <div class="feature">
            <h3>🧠 AI Organization</h3>
            <p>Automatic categorization, tagging, and priority detection</p>
        </div>
        <div class="feature">
            <h3>🔍 Smart Search</h3>
            <p>Find connections between ideas you didn't know existed</p>
        </div>
        <div class="feature">
            <h3>📊 Executive Dashboard</h3>
            <p>See your knowledge growth and priority actions at a glance</p>
        </div>
    </div>
    
    <h2 id="download">Quick Start</h2>
    <pre>
# Download and extract
wget https://iscan.life/download/iscan_life_mvp_v0.1.zip
unzip iscan_life_mvp_v0.1.zip
cd iscan_life

# Install
./setup.sh

# Start using
iscan note       # Add a quick note
iscan dash       # View dashboard
iscan search     # Search your knowledge
    </pre>
    
    <h2>Pricing</h2>
    <p><strong>Beta Access</strong>: Free for first 100 users</p>
    <p><strong>Pro</strong>: $9/month - Unlimited notes, OCR, cloud sync</p>
    <p><strong>Team</strong>: $29/month - Collaboration features</p>
    
    <p style="text-align: center; margin-top: 60px; opacity: 0.6;">
        Powered by Tenxsom AI's Mathematical Intelligence Engine
    </p>
</body>
</html>
'''
        
        with open(self.product_dir / "landing_page.html", 'w') as f:
            f.write(landing_html)
            
        print("✓ Landing page created: products/iscan_life/landing_page.html")


def main():
    packager = IScanLifePackager()
    
    print("iscan.life MVP Packaging")
    print("-" * 40)
    
    # Create package
    packager.create_standalone_package()
    
    # Create landing page
    packager.create_landing_page()
    
    print("\n✓ iscan.life MVP ready for distribution!")
    print("\nNext steps:")
    print("1. Test the package: unzip dist/iscan_life_mvp_v0.1.zip")
    print("2. Register iscan.life domain")
    print("3. Set up landing page hosting")
    print("4. Create demo video")
    print("5. Submit to Product Hunt")


if __name__ == "__main__":
    main()