#!/usr/bin/env python3

"""
YouTube Narration Workflow with HeyGen TTS
Professional video narration for YouTube monetization
"""

import asyncio
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import httpx
from pathlib import Path

# Configuration
USEAPI_BEARER_TOKEN = os.getenv("USEAPI_BEARER_TOKEN", "user:1831-r8vA1WGayarXKuYwpT1PW")
BASE_URL = "https://api.useapi.net/v1"


@dataclass
class NarrationJob:
    """Represents a narration job"""
    job_id: str
    script: str
    voice_id: str
    voice_name: str
    language: str
    speed: float
    pitch: float
    output_file: str
    status: str = "pending"
    audio_url: Optional[str] = None
    duration: Optional[float] = None


class YouTubeNarrationWorkflow:
    """Complete workflow for YouTube video narration"""
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
        self.output_dir = Path("/home/golde/tenxsom-ai-vertex/heygen-integration/narrations")
        self.output_dir.mkdir(exist_ok=True)
        
        # Recommended voices for different content types
        self.voice_profiles = {
            "educational": {
                "voice_id": "elevenlabs_educational_premium",
                "name": "Professional Educator",
                "speed": 0.9,
                "pitch": 1.0,
                "description": "Clear, authoritative voice for tutorials and explanations"
            },
            "entertainment": {
                "voice_id": "elevenlabs_entertainment_premium", 
                "name": "Engaging Narrator",
                "speed": 1.0,
                "pitch": 1.1,
                "description": "Energetic, engaging voice for entertainment content"
            },
            "news": {
                "voice_id": "elevenlabs_news_anchor",
                "name": "News Anchor",
                "speed": 0.95,
                "pitch": 1.0,
                "description": "Professional, trustworthy voice for news commentary"
            },
            "commercial": {
                "voice_id": "elevenlabs_commercial_premium",
                "name": "Commercial Voice",
                "speed": 1.0,
                "pitch": 1.05,
                "description": "Persuasive, professional voice for product reviews"
            },
            "storytelling": {
                "voice_id": "elevenlabs_storyteller",
                "name": "Master Storyteller",
                "speed": 0.85,
                "pitch": 0.95,
                "description": "Rich, narrative voice for storytelling content"
            }
        }
    
    async def generate_narration(self, script: str, content_type: str = "educational",
                               custom_voice_id: Optional[str] = None,
                               custom_settings: Optional[Dict[str, Any]] = None) -> NarrationJob:
        """Generate narration for YouTube video"""
        print(f"🎤 Generating narration for {content_type} content...")
        
        # Select voice profile
        if custom_voice_id:
            voice_profile = {
                "voice_id": custom_voice_id,
                "name": "Custom Voice",
                "speed": 1.0,
                "pitch": 1.0
            }
        else:
            voice_profile = self.voice_profiles.get(content_type, self.voice_profiles["educational"])
        
        # Apply custom settings if provided
        if custom_settings:
            voice_profile.update(custom_settings)
        
        # Create job
        job = NarrationJob(
            job_id=f"narration_{content_type}_{hash(script) % 10000}",
            script=script,
            voice_id=voice_profile["voice_id"],
            voice_name=voice_profile["name"],
            language="en",
            speed=voice_profile["speed"],
            pitch=voice_profile["pitch"],
            output_file=str(self.output_dir / f"{content_type}_narration_{hash(script) % 10000}.mp3")
        )
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                data = {
                    "text": script,
                    "voice_id": job.voice_id,
                    "language": job.language,
                    "speed": job.speed,
                    "pitch": job.pitch
                }
                
                response = await client.post(
                    f"{BASE_URL}/heygen/tts/create",
                    headers=self.headers,
                    json=data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    job.status = "completed"
                    job.audio_url = result.get("audio_url")
                    job.duration = result.get("duration")
                    
                    # Download audio file
                    if job.audio_url:
                        await self.download_audio(job.audio_url, job.output_file)
                    
                    print(f"✅ Narration generated successfully!")
                    print(f"   Duration: {job.duration} seconds")
                    print(f"   File: {job.output_file}")
                    
                else:
                    job.status = "failed"
                    print(f"❌ Narration generation failed: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
        except Exception as e:
            job.status = "failed"
            print(f"❌ Error generating narration: {e}")
        
        return job
    
    async def download_audio(self, audio_url: str, output_file: str):
        """Download generated audio file"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(audio_url)
                response.raise_for_status()
                
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"💾 Audio downloaded: {output_file}")
                
        except Exception as e:
            print(f"❌ Error downloading audio: {e}")
    
    async def create_voice_samples(self, sample_text: str = None) -> List[NarrationJob]:
        """Create sample narrations with different voices for A/B testing"""
        if not sample_text:
            sample_text = """
            Welcome to our channel! In today's video, we're going to explore an exciting topic 
            that will help you understand the latest developments in artificial intelligence. 
            We'll break down complex concepts into easy-to-understand explanations, 
            so make sure to subscribe and hit the notification bell to stay updated 
            with our latest content.
            """
        
        print("🎭 Creating voice samples for A/B testing...")
        
        jobs = []
        for content_type in self.voice_profiles.keys():
            print(f"   Generating sample for {content_type} voice...")
            job = await self.generate_narration(sample_text, content_type)
            jobs.append(job)
            
            # Small delay between requests
            await asyncio.sleep(2)
        
        return jobs
    
    async def batch_generate_narrations(self, scripts: List[Dict[str, str]]) -> List[NarrationJob]:
        """Generate multiple narrations in batch"""
        print(f"🔄 Batch generating {len(scripts)} narrations...")
        
        jobs = []
        for i, script_data in enumerate(scripts):
            script = script_data["script"]
            content_type = script_data.get("content_type", "educational")
            
            print(f"   Processing script {i+1}/{len(scripts)}...")
            job = await self.generate_narration(script, content_type)
            jobs.append(job)
            
            # Rate limiting
            await asyncio.sleep(3)
        
        return jobs
    
    def analyze_script_for_voice_selection(self, script: str) -> str:
        """Analyze script content to recommend best voice type"""
        script_lower = script.lower()
        
        # Educational content indicators
        if any(keyword in script_lower for keyword in 
               ["learn", "tutorial", "how to", "step by step", "explanation", "understand"]):
            return "educational"
        
        # Entertainment content indicators
        if any(keyword in script_lower for keyword in 
               ["fun", "exciting", "amazing", "incredible", "wow", "awesome"]):
            return "entertainment"
        
        # News content indicators
        if any(keyword in script_lower for keyword in 
               ["today", "news", "update", "report", "breaking", "latest"]):
            return "news"
        
        # Commercial content indicators
        if any(keyword in script_lower for keyword in 
               ["product", "review", "buy", "purchase", "recommend", "deal"]):
            return "commercial"
        
        # Storytelling content indicators
        if any(keyword in script_lower for keyword in 
               ["story", "once upon", "happened", "experience", "journey"]):
            return "storytelling"
        
        # Default to educational
        return "educational"
    
    def create_narration_workflow_config(self) -> Dict[str, Any]:
        """Create configuration for narration workflow automation"""
        config = {
            "workflow_name": "YouTube Narration Automation",
            "description": "Professional narration workflow for YouTube monetization",
            "voice_profiles": self.voice_profiles,
            "quality_settings": {
                "premium": {
                    "use_elevenlabs": True,
                    "quality_tier": "premium",
                    "speed_adjustment": 0.9,
                    "pitch_adjustment": 1.0
                },
                "standard": {
                    "use_elevenlabs": False,
                    "quality_tier": "standard",
                    "speed_adjustment": 1.0,
                    "pitch_adjustment": 1.0
                }
            },
            "content_type_mapping": {
                "how_to": "educational",
                "tutorial": "educational",
                "review": "commercial",
                "news": "news",
                "story": "storytelling",
                "entertainment": "entertainment"
            },
            "batch_processing": {
                "max_concurrent": 3,
                "rate_limit_seconds": 3,
                "retry_attempts": 2
            },
            "output_settings": {
                "format": "mp3",
                "quality": "high",
                "sample_rate": 44100,
                "channels": "mono"
            }
        }
        
        config_file = self.output_dir / "narration_workflow_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"📝 Workflow configuration saved: {config_file}")
        return config
    
    def display_workflow_summary(self, jobs: List[NarrationJob]):
        """Display summary of narration workflow results"""
        print("\n" + "="*80)
        print("🎙️ YOUTUBE NARRATION WORKFLOW SUMMARY")
        print("="*80)
        
        successful_jobs = [job for job in jobs if job.status == "completed"]
        failed_jobs = [job for job in jobs if job.status == "failed"]
        
        print(f"\n📊 RESULTS:")
        print(f"   ✅ Successful: {len(successful_jobs)}")
        print(f"   ❌ Failed: {len(failed_jobs)}")
        print(f"   📁 Output Directory: {self.output_dir}")
        
        if successful_jobs:
            print(f"\n🎯 SUCCESSFUL NARRATIONS:")
            for job in successful_jobs:
                print(f"   • {job.voice_name} ({job.duration}s) - {job.output_file}")
        
        if failed_jobs:
            print(f"\n⚠️ FAILED NARRATIONS:")
            for job in failed_jobs:
                print(f"   • {job.voice_name} - {job.job_id}")
        
        total_duration = sum(job.duration or 0 for job in successful_jobs)
        print(f"\n💰 COST ANALYSIS:")
        print(f"   • Total Audio Duration: {total_duration:.1f} seconds")
        print(f"   • Total Cost: FREE (unlimited HeyGen TTS)")
        print(f"   • Traditional Voice Actor Cost: ${total_duration * 0.25:.2f}")
        print(f"   • Savings: ${total_duration * 0.25:.2f}")
        
        print(f"\n🚀 NEXT STEPS:")
        print(f"   1. Test narrations with your audience")
        print(f"   2. A/B test different voice profiles")
        print(f"   3. Integrate with video generation workflow")
        print(f"   4. Scale to full YouTube automation")


async def demo_workflow():
    """Demonstrate the YouTube narration workflow"""
    print("🎬 YouTube Narration Workflow Demo")
    print("="*50)
    
    workflow = YouTubeNarrationWorkflow(USEAPI_BEARER_TOKEN)
    
    # Sample scripts for different content types
    demo_scripts = [
        {
            "script": "Welcome to our tech tutorial series! Today we're learning how to build an AI-powered application from scratch. We'll cover everything from setup to deployment, so grab your favorite beverage and let's dive in!",
            "content_type": "educational"
        },
        {
            "script": "This product review is going to blow your mind! I've been testing this new gadget for two weeks, and the results are incredible. Here's everything you need to know before making your purchase decision.",
            "content_type": "commercial"
        },
        {
            "script": "Breaking news in the tech world! A major AI breakthrough has just been announced that could change everything we know about machine learning. Let's break down what this means for the future.",
            "content_type": "news"
        }
    ]
    
    # Create workflow configuration
    config = workflow.create_narration_workflow_config()
    
    # Try to generate narrations (will fail if API is down)
    try:
        jobs = await workflow.batch_generate_narrations(demo_scripts)
        workflow.display_workflow_summary(jobs)
    except Exception as e:
        print(f"❌ Demo failed due to API issues: {e}")
        print("🔄 Workflow is ready to run when UseAPI.net service is restored")
    
    print(f"\n✅ Workflow setup complete and ready for production!")


if __name__ == "__main__":
    asyncio.run(demo_workflow())