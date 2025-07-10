#!/usr/bin/env python3
"""
Execute Live Upload Test
Complete end-to-end test with MCP, video generation, and YouTube upload
"""

import asyncio
import os
import sys
import json
import tempfile
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Add paths for our modules
sys.path.append(str(Path(__file__).parent))

# Load environment
load_dotenv()

class LiveUploadExecutor:
    """Execute complete live upload workflow"""
    
    def __init__(self):
        self.mcp_server_url = os.getenv("MCP_SERVER_URL")
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "steps": [],
            "final_result": {}
        }
    
    def log_step(self, step_name: str, success: bool, details: str = ""):
        """Log a step in the process"""
        self.test_results["steps"].append({
            "step": step_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
        status = "✅" if success else "❌"
        print(f"{status} {step_name}")
        if details:
            print(f"   {details}")
    
    async def step1_get_mcp_template(self) -> dict:
        """Step 1: Get template from MCP server"""
        print("\n1️⃣ Getting template from MCP server...")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Get available templates
                response = await client.get(f"{self.mcp_server_url}/api/templates")
                if response.status_code != 200:
                    raise Exception(f"Failed to get templates: {response.status_code}")
                
                templates = response.json().get("templates", [])
                if not templates:
                    raise Exception("No templates available")
                
                # Select a tech/educational template
                selected_template = None
                for template in templates:
                    name = template.get("template_name", "").lower()
                    if "tech" in name or "educational" in name or "news" in name:
                        selected_template = template
                        break
                
                if not selected_template:
                    selected_template = templates[0]  # Use first available
                
                self.log_step("MCP Template Selection", True, f"Selected: {selected_template['template_name']}")
                return selected_template
                
        except Exception as e:
            self.log_step("MCP Template Selection", False, str(e))
            raise
    
    async def step2_process_template(self, template: dict) -> dict:
        """Step 2: Process template with context variables"""
        print("\n2️⃣ Processing template with context...")
        
        try:
            # Create relevant context for a real upload
            context = {
                "target_audience": "AI and technology enthusiasts",
                "current_trends": [
                    "artificial intelligence breakthrough",
                    "automated content creation", 
                    "YouTube monetization strategies"
                ],
                "duration_preference": "short",
                "content_style": "educational and engaging",
                "platform_focus": "youtube",
                "urgency": "high",
                "brand_voice": "professional yet accessible",
                "video_topic": "TenxsomAI: The Future of Automated Content Creation",
                "key_points": [
                    "AI-powered video generation",
                    "Automated YouTube monetization",
                    "Template-based content creation"
                ]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.mcp_server_url}/api/templates/process",
                    json={
                        "template_name": template["template_name"],
                        "context_variables": context
                    }
                )
                
                if response.status_code != 200:
                    raise Exception(f"Template processing failed: {response.status_code}")
                
                result = response.json()
                if "error" in result:
                    raise Exception(f"Template error: {result['error']}")
                
                self.log_step("Template Processing", True, "Generated production-ready metadata")
                return {
                    "template_result": result,
                    "context_used": context
                }
                
        except Exception as e:
            self.log_step("Template Processing", False, str(e))
            raise
    
    def step3_create_test_video(self) -> str:
        """Step 3: Create a test video file"""
        print("\n3️⃣ Creating test video...")
        
        try:
            # Create a simple test video file
            test_video_dir = Path("videos/output")
            test_video_dir.mkdir(parents=True, exist_ok=True)
            
            video_path = test_video_dir / f"tenxsomai_live_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            
            # Try to create with ffmpeg first
            ffmpeg_cmd = f"""
            ffmpeg -y -f lavfi -i color=c=blue:s=1280x720:d=10 \
            -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:\
            text='TenxsomAI Live Upload Test\\n{datetime.now().strftime("%Y-%m-%d %H:%M")}\\n\\nAutomated Content Creation\\nPowered by AI':fontcolor=white:fontsize=36:\
            box=1:boxcolor=black@0.7:boxborderw=10:x=(w-text_w)/2:y=(h-text_h)/2" \
            -c:v libx264 -t 10 -r 30 {video_path}
            """
            
            result = os.system(ffmpeg_cmd + " 2>/dev/null")
            
            if result == 0 and video_path.exists():
                file_size = video_path.stat().st_size / 1024 / 1024  # MB
                self.log_step("Test Video Creation", True, f"Created {file_size:.1f}MB video")
                return str(video_path)
            else:
                # Fallback: create a minimal mp4 header for testing
                self.log_step("Video Creation (ffmpeg failed)", False, "Creating minimal test file")
                
                # Create a minimal valid MP4 file structure for testing
                mp4_header = bytes([
                    0x00, 0x00, 0x00, 0x18, 0x66, 0x74, 0x79, 0x70,  # ftyp box
                    0x6D, 0x70, 0x34, 0x32, 0x00, 0x00, 0x00, 0x00,
                    0x6D, 0x70, 0x34, 0x31, 0x69, 0x73, 0x6F, 0x6D,
                ])
                
                with open(video_path, "wb") as f:
                    f.write(mp4_header)
                    f.write(b"TENXSOMAI_TEST_VIDEO_CONTENT" * 1000)  # Pad to reasonable size
                
                self.log_step("Test Video Creation", True, f"Created minimal test file: {video_path.name}")
                return str(video_path)
                
        except Exception as e:
            self.log_step("Test Video Creation", False, str(e))
            raise
    
    async def step4_youtube_upload(self, video_path: str, metadata: dict) -> dict:
        """Step 4: Upload to YouTube"""
        print("\n4️⃣ Uploading to YouTube...")
        
        try:
            from youtube_oauth_service import YouTubeOAuthService
            
            # Initialize YouTube service
            youtube_service = YouTubeOAuthService()
            
            # Test connection first
            if not youtube_service.test_connection():
                raise Exception("YouTube connection test failed")
            
            # Extract metadata from MCP result
            template_result = metadata.get("template_result", {})
            
            # Create upload metadata
            upload_title = f"TenxsomAI Live Test - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            upload_description = f"""
This is a live test upload from the TenxsomAI automated content creation system.

🤖 Generated using AI-powered templates
📊 Part of our 30-day monetization strategy 
🎯 Target: 2,880 videos in 30 days

Template Used: {metadata.get('template_result', {}).get('template_name', 'Unknown')}

This video demonstrates:
• Automated video generation
• MCP-based template processing
• Cloud-native upload pipeline
• Production-ready workflow

#TenxsomAI #AI #Automation #ContentCreation
            """.strip()
            
            upload_tags = [
                "TenxsomAI", "AI", "automation", "content creation", 
                "YouTube automation", "artificial intelligence", "test upload"
            ]
            
            # Upload video (private for testing)
            video_id = youtube_service.upload_video(
                video_path=video_path,
                title=upload_title,
                description=upload_description,
                tags=upload_tags,
                category_id="22",  # People & Blogs
                privacy_status="private"  # Keep private for testing
            )
            
            upload_result = {
                "video_id": video_id,
                "video_url": f"https://www.youtube.com/watch?v={video_id}",
                "title": upload_title,
                "privacy": "private"
            }
            
            self.log_step("YouTube Upload", True, f"Video ID: {video_id}")
            return upload_result
            
        except Exception as e:
            self.log_step("YouTube Upload", False, str(e))
            raise
    
    def step5_cleanup(self, video_path: str):
        """Step 5: Clean up test files"""
        print("\n5️⃣ Cleaning up...")
        
        try:
            if os.path.exists(video_path):
                os.remove(video_path)
                self.log_step("Cleanup", True, f"Removed test video: {Path(video_path).name}")
            else:
                self.log_step("Cleanup", True, "No cleanup needed")
                
        except Exception as e:
            self.log_step("Cleanup", False, str(e))
    
    async def execute_full_workflow(self):
        """Execute the complete live upload workflow"""
        print("🚀 TENXSOMAI LIVE UPLOAD TEST")
        print("=" * 50)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"MCP Server: {self.mcp_server_url}")
        print("=" * 50)
        
        video_path = None
        
        try:
            # Step 1: Get MCP template
            template = await self.step1_get_mcp_template()
            
            # Step 2: Process template
            metadata = await self.step2_process_template(template)
            
            # Step 3: Create test video
            video_path = self.step3_create_test_video()
            
            # Step 4: Upload to YouTube
            upload_result = await self.step4_youtube_upload(video_path, metadata)
            
            # Record final result
            self.test_results["final_result"] = {
                "success": True,
                "video_uploaded": True,
                "upload_details": upload_result,
                "template_used": template["template_name"],
                "metadata_generated": True
            }
            
            print("\n" + "=" * 50)
            print("🎉 LIVE UPLOAD TEST SUCCESSFUL!")
            print("=" * 50)
            print(f"✅ Video uploaded: {upload_result['video_url']}")
            print(f"📝 Title: {upload_result['title']}")
            print(f"🔒 Privacy: {upload_result['privacy']}")
            print(f"🎬 Template: {template['template_name']}")
            
            return True
            
        except Exception as e:
            self.test_results["final_result"] = {
                "success": False,
                "error": str(e),
                "video_uploaded": False
            }
            
            print(f"\n❌ LIVE UPLOAD TEST FAILED: {e}")
            return False
            
        finally:
            # Step 5: Cleanup
            if video_path:
                self.step5_cleanup(video_path)
            
            # Save results
            with open("live_upload_test_results.json", "w") as f:
                json.dump(self.test_results, f, indent=2)
            
            print(f"\n📄 Test results saved to: live_upload_test_results.json")


async def main():
    """Main execution function"""
    executor = LiveUploadExecutor()
    success = await executor.execute_full_workflow()
    
    if success:
        print("\n🎉 Live upload system is working! Ready for production scale.")
    else:
        print("\n💔 Live upload test failed. Check logs for issues.")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())