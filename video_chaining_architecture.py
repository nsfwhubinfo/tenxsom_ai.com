#!/usr/bin/env python3

"""
Video Chaining Architecture for LTX Studio Integration
Handles concatenation of multiple 5-second segments into full-length videos
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
import subprocess
import tempfile
import os

logger = logging.getLogger(__name__)

@dataclass
class VideoSegment:
    """Individual 5-second video segment"""
    segment_id: str
    video_url: str
    local_path: str
    duration: float
    scene_id: str
    prompt: str
    start_time: float
    end_time: float

@dataclass
class VideoChainRequest:
    """Request for chaining multiple segments into final video"""
    content_id: str
    template_name: str
    target_duration: int
    scenes: List[Dict[str, Any]]
    aspect_ratio: str = "16:9"
    output_quality: str = "high"

@dataclass
class ChainedVideoResult:
    """Result of video chaining operation"""
    content_id: str
    final_video_path: str
    total_duration: float
    segments_used: int
    success: bool
    error_message: str = None

class VideoChainOrchestrator:
    """
    Orchestrates the creation of full-length videos from LTX Studio 5-second segments
    """
    
    def __init__(self, enhanced_router, temp_dir: str = "/tmp/video_chains"):
        self.enhanced_router = enhanced_router
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
    async def generate_chained_video(self, request: VideoChainRequest) -> ChainedVideoResult:
        """
        Generate a full-length video by chaining multiple LTX Studio segments
        
        Strategy:
        1. Break template scenes into 5-second segments
        2. Generate each segment via LTX Studio
        3. Download all video segments
        4. Concatenate using FFmpeg
        5. Apply transitions and audio sync
        """
        try:
            # Step 1: Plan segment generation
            segments_plan = self._plan_segments(request)
            logger.info(f"Planned {len(segments_plan)} segments for {request.content_id}")
            
            # Step 2: Generate all segments
            video_segments = await self._generate_segments(segments_plan)
            logger.info(f"Generated {len(video_segments)} video segments")
            
            # Step 3: Download video files
            downloaded_segments = await self._download_segments(video_segments)
            logger.info(f"Downloaded {len(downloaded_segments)} video files")
            
            # Step 4: Concatenate videos
            final_video_path = await self._concatenate_videos(request, downloaded_segments)
            logger.info(f"Created final video: {final_video_path}")
            
            return ChainedVideoResult(
                content_id=request.content_id,
                final_video_path=final_video_path,
                total_duration=sum(seg.duration for seg in downloaded_segments),
                segments_used=len(downloaded_segments),
                success=True
            )
            
        except Exception as e:
            logger.error(f"Video chaining failed for {request.content_id}: {e}")
            return ChainedVideoResult(
                content_id=request.content_id,
                final_video_path="",
                total_duration=0,
                segments_used=0,
                success=False,
                error_message=str(e)
            )
    
    def _plan_segments(self, request: VideoChainRequest) -> List[Dict[str, Any]]:
        """
        Break down template scenes into 5-second segments for LTX Studio
        """
        segments = []
        segment_id = 0
        
        for scene in request.scenes:
            scene_duration = scene.get('duration_seconds', 5)
            scene_prompt = scene.get('resolved_video_prompts', [{}])[0].get('prompt', '')
            
            # Calculate how many 5-second segments needed
            num_segments = max(1, (scene_duration + 4) // 5)  # Round up
            
            for i in range(num_segments):
                start_time = i * 5
                end_time = min(start_time + 5, scene_duration)
                
                # Create segment-specific prompt
                segment_prompt = self._create_segment_prompt(scene_prompt, i, num_segments)
                
                segments.append({
                    'segment_id': f"{request.content_id}_seg_{segment_id:03d}",
                    'scene_id': scene.get('scene_id'),
                    'prompt': segment_prompt,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': min(5, scene_duration - start_time)
                })
                segment_id += 1
        
        return segments
    
    def _create_segment_prompt(self, base_prompt: str, segment_index: int, total_segments: int) -> str:
        """
        Create segment-specific prompts to ensure continuity
        """
        if total_segments == 1:
            return base_prompt
        
        # Add temporal context for multi-segment scenes
        if segment_index == 0:
            return f"Opening shot: {base_prompt}"
        elif segment_index == total_segments - 1:
            return f"Concluding shot: {base_prompt}"
        else:
            return f"Continuing shot {segment_index + 1}: {base_prompt}"
    
    async def _generate_segments(self, segments_plan: List[Dict[str, Any]]) -> List[VideoSegment]:
        """
        Generate all video segments using LTX Studio
        """
        from integrations.enhanced_model_router import GenerationRequest, Platform, QualityTier
        
        video_segments = []
        
        # Generate segments in parallel batches
        batch_size = 3  # Avoid overwhelming LTX Studio
        
        for i in range(0, len(segments_plan), batch_size):
            batch = segments_plan[i:i + batch_size]
            batch_tasks = []
            
            for segment_data in batch:
                request = GenerationRequest(
                    prompt=segment_data['prompt'],
                    platform=Platform.YOUTUBE,
                    quality_tier=QualityTier.VOLUME,  # Use LTX Studio
                    duration=5,  # Fixed LTX Studio duration
                    aspect_ratio="16:9"
                )
                
                task = self.enhanced_router.generate_video(request)
                batch_tasks.append((task, segment_data))
            
            # Wait for batch completion
            for task, segment_data in batch_tasks:
                try:
                    response = await task
                    
                    if response.success and response.download_url:
                        video_segments.append(VideoSegment(
                            segment_id=segment_data['segment_id'],
                            video_url=response.download_url,
                            local_path="",  # Will be set during download
                            duration=5.0,
                            scene_id=segment_data['scene_id'],
                            prompt=segment_data['prompt'],
                            start_time=segment_data['start_time'],
                            end_time=segment_data['end_time']
                        ))
                        
                except Exception as e:
                    logger.error(f"Segment generation failed: {e}")
            
            # Brief pause between batches
            await asyncio.sleep(2)
        
        return video_segments
    
    async def _download_segments(self, video_segments: List[VideoSegment]) -> List[VideoSegment]:
        """
        Download all video segment files locally
        """
        import aiohttp
        
        downloaded_segments = []
        
        async with aiohttp.ClientSession() as session:
            for segment in video_segments:
                try:
                    # Create local file path
                    local_path = self.temp_dir / f"{segment.segment_id}.mp4"
                    
                    # Download video file
                    async with session.get(segment.video_url) as response:
                        if response.status == 200:
                            with open(local_path, 'wb') as f:
                                async for chunk in response.content.iter_chunked(8192):
                                    f.write(chunk)
                            
                            # Update segment with local path
                            segment.local_path = str(local_path)
                            downloaded_segments.append(segment)
                            logger.info(f"Downloaded: {segment.segment_id}")
                        else:
                            logger.error(f"Download failed for {segment.segment_id}: {response.status}")
                            
                except Exception as e:
                    logger.error(f"Download error for {segment.segment_id}: {e}")
        
        return downloaded_segments
    
    async def _concatenate_videos(self, request: VideoChainRequest, segments: List[VideoSegment]) -> str:
        """
        Concatenate video segments using FFmpeg
        """
        if not segments:
            raise Exception("No video segments to concatenate")
        
        # Create output path
        output_path = self.temp_dir / f"{request.content_id}_final.mp4"
        
        # Create FFmpeg concat file
        concat_file = self.temp_dir / f"{request.content_id}_concat.txt"
        
        # Sort segments by start time
        sorted_segments = sorted(segments, key=lambda x: x.start_time)
        
        # Write concat file
        with open(concat_file, 'w') as f:
            for segment in sorted_segments:
                f.write(f"file '{segment.local_path}'\n")
        
        # FFmpeg command with smooth transitions
        ffmpeg_cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-movflags', '+faststart',
            '-preset', 'medium',
            '-crf', '23',
            '-y',  # Overwrite output file
            str(output_path)
        ]
        
        # Execute FFmpeg
        try:
            result = subprocess.run(
                ffmpeg_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"Video concatenation successful: {output_path}")
                return str(output_path)
            else:
                raise Exception(f"FFmpeg failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Video concatenation timed out")
        except Exception as e:
            raise Exception(f"Video concatenation error: {e}")
    
    async def cleanup_temp_files(self, content_id: str):
        """Clean up temporary files for a content ID"""
        try:
            import glob
            temp_files = glob.glob(str(self.temp_dir / f"{content_id}*"))
            for file_path in temp_files:
                os.remove(file_path)
            logger.info(f"Cleaned up temp files for {content_id}")
        except Exception as e:
            logger.error(f"Cleanup error for {content_id}: {e}")

# Usage Example
async def demonstrate_video_chaining():
    """
    Example of how video chaining would work with templates
    """
    from integrations.enhanced_model_router import EnhancedModelRouter
    
    # Initialize components
    router = EnhancedModelRouter(...)  # Your router config
    chain_orchestrator = VideoChainOrchestrator(router)
    
    # Example: Documentary Mystery template requiring 120-second video
    chain_request = VideoChainRequest(
        content_id="doc_mystery_001",
        template_name="Documentary_Mystery_LEMMiNO_Style_v1",
        target_duration=120,
        scenes=[
            {
                "scene_id": "01_mysterious_opening",
                "duration_seconds": 25,
                "resolved_video_prompts": [{
                    "prompt": "Dark, atmospheric shot of an abandoned building at twilight"
                }]
            },
            {
                "scene_id": "02_evidence_presentation", 
                "duration_seconds": 45,
                "resolved_video_prompts": [{
                    "prompt": "Close-up of mysterious documents and evidence on a desk"
                }]
            },
            {
                "scene_id": "03_investigation",
                "duration_seconds": 30,
                "resolved_video_prompts": [{
                    "prompt": "Investigator examining clues with dramatic lighting"
                }]
            },
            {
                "scene_id": "04_conclusion",
                "duration_seconds": 20,
                "resolved_video_prompts": [{
                    "prompt": "Wide shot revealing the truth with dramatic music"
                }]
            }
        ]
    )
    
    # Generate chained video
    result = await chain_orchestrator.generate_chained_video(chain_request)
    
    if result.success:
        print(f"✅ Generated {result.total_duration}s video from {result.segments_used} segments")
        print(f"📹 Final video: {result.final_video_path}")
    else:
        print(f"❌ Video chaining failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(demonstrate_video_chaining())