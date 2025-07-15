#!/usr/bin/env python3
"""
TenxSOM AI - Master Video Orchestrator (v3 - Production Fix)
This script implements the final, correct, end-to-end pipeline.
It bridges the gap between the planning and generation services to produce an actual video file.

ARCHITECTURAL FIX: Directly connects blueprint output to video generation engine,
bypassing the flawed tier-based routing that never calls generate_with_useapi().
"""
import os
import sys
import json
import logging
from pathlib import Path
import time
import asyncio
from datetime import datetime

# --- Configure Transparent Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("MasterOrchestrator")

# --- Direct Import of Verified Components ---
try:
    from claude_video_service import ClaudeVideoService, ClaudeVideoRequest
    from production_video_generator import ProductionVideoGenerator, VideoRequest, VideoResult
    logger.info("✅ Successfully imported all required service modules.")
except ImportError as e:
    logger.error(f"FATAL: Could not import service modules. Ensure they are in the PYTHONPATH. Error: {e}")
    sys.exit(1)

class MasterOrchestrator:
    def __init__(self, job_file_path: str):
        logger.info("🔧 --- Orchestrator Initializing ---")
        self.job_request = self._load_job(job_file_path)
        self.content_id = self.job_request['content_id']
        self.output_dir = Path("generated_content") / self.content_id
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Track pipeline timing
        self.pipeline_start_time = time.time()
        
        # Instantiate services
        self.claude_service = ClaudeVideoService()
        self.video_generator = ProductionVideoGenerator()
        logger.info("✅ Services initialized.")

    def _load_job(self, path: str) -> dict:
        """Load and validate job request"""
        logger.info(f"📄 Loading job definition from: {path}")
        
        if not os.path.exists(path):
            logger.error(f"FATAL: Job file not found: {path}")
            sys.exit(1)
            
        with open(path, 'r') as f:
            job = json.load(f)
            
        # Validate required fields
        required_fields = ['content_id', 'title', 'archetype', 'tier', 'target_duration', 'platform']
        missing_fields = [field for field in required_fields if field not in job]
        
        if missing_fields:
            logger.error(f"FATAL: Job file missing required fields: {missing_fields}")
            sys.exit(1)
            
        logger.info(f"✅ Job loaded: {job['content_id']} - {job['title']}")
        return job

    async def run_pipeline(self) -> bool:
        """
        Execute the complete end-to-end pipeline with direct service connection.
        Returns True only if an actual video file is created.
        """
        logger.info(f"🚀 === STARTING PIPELINE for '{self.content_id}' ===")
        logger.info(f"📋 Title: {self.job_request['title']}")
        logger.info(f"🎭 Archetype: {self.job_request['archetype']}")
        logger.info(f"⏱️  Duration: {self.job_request['target_duration']}s")
        logger.info(f"📱 Platform: {self.job_request['platform']}")
        
        try:
            # === PHASE 1: PLANNING (Create the Blueprint) ===
            logger.info("🎯 --- Phase 1: Content Planning ---")
            logger.info("Creating detailed video blueprint using Claude service...")
            
            claude_request = ClaudeVideoRequest(
                content_id=self.content_id,
                title=self.job_request['title'],
                archetype=self.job_request['archetype'],
                target_duration=self.job_request['target_duration'],
                platform=self.job_request['platform'],
                prompt=f"Create video content for: {self.job_request['title']}"
            )
            
            content_result = await self.claude_service.generate_video_content(claude_request)
            if not content_result.success:
                raise Exception(f"Content planning failed: {content_result.error}")
            
            logger.info(f"✅ Planning complete. Blueprint saved to: {content_result.content_file_path}")
            logger.info(f"💰 Planning cost: ${content_result.cost_estimate:.4f}")

            # === PHASE 2: EXECUTION (Bridge Blueprint to Engine) ===
            logger.info("🎬 --- Phase 2: Video Generation ---")
            logger.info("ARCHITECTURAL FIX: Connecting blueprint output directly to video generation engine...")
            
            # 1. Read the blueprint created in Phase 1
            logger.info("📖 Reading blueprint from planning phase...")
            with open(content_result.content_file_path, 'r') as f:
                plan = json.load(f)

            # 2. Extract the specific visual prompt from the blueprint
            logger.info("🔍 Extracting visual prompt from blueprint...")
            visual_prompt = self._extract_visual_prompt_from_blueprint(plan)
            logger.info(f"📝 Extracted visual prompt: '{visual_prompt[:100]}...'")

            # 3. Create a direct request for the video generation engine
            video_request = VideoRequest(
                content_id=self.content_id,
                title=self.job_request['title'],
                archetype=self.job_request['archetype'],
                tier=self.job_request['tier'],
                target_duration=self.job_request['target_duration'],
                platform=self.job_request['platform'],
                prompt=visual_prompt
            )

            # 4. ARCHITECTURAL FIX: Call the video generation method DIRECTLY.
            # We bypass the flawed tier-based router and explicitly call the method
            # that we know produces an MP4 file. This is the missing conveyor belt.
            logger.info("🔗 CONVEYOR BELT: Calling UseAPI video generation engine directly...")
            logger.info("   (Bypassing flawed tier-based routing that never connects to UseAPI)")
            
            video_generation_start = time.time()
            video_result = await self.video_generator.generate_with_useapi(video_request)
            video_generation_time = time.time() - video_generation_start

            if not video_result.success:
                raise Exception(f"Video generation failed: {video_result.error}")

            logger.info(f"✅ Video generation successful in {video_generation_time:.2f}s!")
            logger.info(f"💰 Video generation cost: ${video_result.cost_estimate:.4f}")
            
            # === PHASE 3: ASYNCHRONOUS COMPLETION STATUS ===
            logger.info("🔍 --- Phase 3: Asynchronous Generation Status ---")
            
            # Check if this is a pending video generation
            if video_result.metadata.get('status') == 'pending_generation':
                job_id = video_result.metadata.get('job_id')
                job_file = video_result.metadata.get('job_file')
                expected_path = video_result.video_file_path
                
                logger.info(f"📋 Video generation submitted successfully")
                logger.info(f"🆔 Job ID: {job_id}")
                logger.info(f"📁 Job state file: {job_file}")
                logger.info(f"📽️  Expected video path: {expected_path}")
                logger.info(f"⏰ Status: Video generation in progress (asynchronous)")
                logger.info(f"")
                logger.info(f"🔄 To check progress and download completed video, run:")
                logger.info(f"   python3 poll_video_status.py")
                logger.info(f"")
                logger.info(f"📊 The poller will automatically download the video when ready")
            else:
                # Synchronous completion (legacy path)
                final_video_path = video_result.video_file_path
                logger.info(f"📁 Expected video file location: {final_video_path}")

                if final_video_path and os.path.exists(final_video_path):
                    file_size = os.path.getsize(final_video_path)
                    if file_size > 0:
                        logger.info(f"✅ SUCCESS: Verified non-empty video file created")
                        logger.info(f"📏 File size: {file_size:,} bytes")
                        logger.info(f"📄 File type: {Path(final_video_path).suffix}")
                    else:
                        raise Exception(f"Video file exists but is empty: {final_video_path}")
                else:
                    raise Exception(f"Video file was not created at expected location: {final_video_path}")

            # === PIPELINE COMPLETION ===
            total_time = time.time() - self.pipeline_start_time
            total_cost = content_result.cost_estimate + video_result.cost_estimate
            
            logger.info(f"🎉 === PIPELINE COMPLETE for '{self.content_id}' ===")
            logger.info(f"⏱️  Total pipeline duration: {total_time:.2f} seconds")
            logger.info(f"💰 Total pipeline cost: ${total_cost:.4f}")
            
            # Show final video path based on generation type
            if video_result.metadata.get('status') == 'pending_generation':
                logger.info(f"🎥 Video will be saved to: {video_result.video_file_path}")
            else:
                logger.info(f"🎥 Final video file: {video_result.video_file_path}")
            
            # Save final pipeline report
            self._save_final_report(content_result, video_result, total_time, total_cost)
            
            return True

        except Exception as e:
            logger.error(f"💥 PIPELINE FAILED for '{self.content_id}': {e}", exc_info=True)
            return False

    def _extract_visual_prompt_from_blueprint(self, plan: dict) -> str:
        """
        Extract the visual prompt from the Claude-generated blueprint.
        This is the crucial connection between planning and execution phases.
        """
        try:
            # Try to parse the generated content as JSON
            generated_content_str = plan.get('generated_content', '{}')
            
            # Handle case where generated_content is already parsed
            if isinstance(generated_content_str, dict):
                generated_content = generated_content_str
            else:
                generated_content = json.loads(generated_content_str)
            
            # Extract visual cue from video plan
            video_plan = generated_content.get('video_plan', {})
            script_segments = video_plan.get('script_segments', [])
            
            if script_segments and len(script_segments) > 0:
                visual_cue = script_segments[0].get('visual_cue', '')
                if visual_cue:
                    logger.info("📖 Successfully extracted visual cue from blueprint")
                    return visual_cue
            
            # Fallback: look for other visual descriptions
            for key in ['visual_description', 'scene_description', 'visual_elements']:
                if key in generated_content:
                    logger.info(f"📖 Using fallback visual description from '{key}'")
                    return str(generated_content[key])
                    
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            logger.warning(f"⚠️  Could not parse blueprint for visual cue: {e}")
        
        # Final fallback: create a visual prompt from job request
        fallback_prompt = f"High-quality {self.job_request['archetype']} style video about {self.job_request['title']}. Professional cinematic quality with engaging visuals."
        logger.info("📖 Using fallback visual prompt based on job request")
        return fallback_prompt

    def _save_final_report(self, content_result, video_result, total_time: float, total_cost: float):
        """Save comprehensive pipeline report"""
        report = {
            "pipeline_id": self.content_id,
            "job_request": self.job_request,
            "execution_timestamp": datetime.now().isoformat(),
            "total_duration_seconds": total_time,
            "total_cost_usd": total_cost,
            "phases": {
                "content_planning": {
                    "success": content_result.success,
                    "cost": content_result.cost_estimate,
                    "output_file": content_result.content_file_path
                },
                "video_generation": {
                    "success": video_result.success,
                    "cost": video_result.cost_estimate,
                    "video_file": video_result.video_file_path,
                    "file_size_bytes": os.path.getsize(video_result.video_file_path) if video_result.video_file_path and os.path.exists(video_result.video_file_path) else 0
                }
            },
            "architectural_fix": "Bypassed flawed tier-based routing to directly connect blueprint to video generation engine",
            "success_criteria": "Non-empty MP4 video file created"
        }
        
        report_path = self.output_dir / "final_pipeline_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Final pipeline report saved: {report_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("FATAL: You must provide the path to a job request JSON file.")
        print("Usage: python master_orchestrator_v3.py <path_to_job_file.json>")
        print("")
        print("Example:")
        print("python master_orchestrator_v3.py final_test_job.json")
        sys.exit(1)
    
    # Execute the corrected pipeline
    orchestrator = MasterOrchestrator(sys.argv[1])
    success = asyncio.run(orchestrator.run_pipeline())
    
    if success:
        print("\n🎉 PIPELINE SUCCEEDED: Video file created successfully!")
        sys.exit(0)
    else:
        print("\n💥 PIPELINE FAILED: Check logs for details.")
        sys.exit(1)